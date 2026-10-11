import requests
import logging

from wp1 import zimfarm
from wp1.config import get_settings
from wp1.logic import zim_schedules
from wp1.models.wp10.zim_file import ZimTask
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.templates import env as jinja_env
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)


def send_zim_ready_email(
    recipient_username,
    recipient_email,
    zim_title,
    download_url,
    manage_schedule_url=None,
    unsubscribe_url=None,
    next_generation_months=None,
):
    """Sends an email notification when a ZIM file is ready for download."""

    settings = get_settings()
    if not settings.MAILGUN_API_KEY:
        logger.warning("Mailgun not configured. Email not sent.")
        return False

    template = jinja_env.get_template("generated-scheduled-zim-email.html.jinja2")

    context = {
        "user": recipient_username,
        "title": zim_title,
        "download_url": download_url,
        "manage_schedule_url": manage_schedule_url or "#",
        "unsubscribe_url": unsubscribe_url or "#",
        "block_email": unsubscribe_url or "#",
        "next_generation_months": next_generation_months,
    }

    html_content = template.render(**context)

    email_data = {
        "from": "Wikipedia WP 1.0 Project <notifications@mg.wp1.openzim.org>",
        "to": f"{recipient_username} <{recipient_email}>",
        "subject": f"Your ZIM File is Ready for Download - {zim_title}",
        "text": f"Hello {recipient_username},\n\nYour ZIM file '{zim_title}' is ready for download at {download_url}.",
        "html": html_content,
    }

    return _send_email(email_data)


def send_zim_failed_email(
    recipient_username,
    recipient_email,
    zim_title,
    schedule_ended,
    manage_schedule_url=None,
    unsubscribe_url=None,
):
    """Sends an email notification when a scheduled ZIM file could not be generated."""

    settings = get_settings()
    if not settings.MAILGUN_API_KEY:
        logger.warning("Mailgun not configured. Email not sent.")
        return False

    template = jinja_env.get_template("failed-scheduled-zim-email.html.jinja2")

    context = {
        "user": recipient_username,
        "title": zim_title,
        "schedule_ended": schedule_ended,
        "manage_schedule_url": manage_schedule_url or "#",
        "unsubscribe_url": unsubscribe_url or "#",
    }

    html_content = template.render(**context)

    text = f"Hello {recipient_username},\n\nYour scheduled ZIM file '{zim_title}' could not be generated."
    if schedule_ended:
        text += (
            " Your schedule has stopped and no more ZIM files will be generated for it."
        )

    email_data = {
        "from": "Wikipedia WP 1.0 Project <notifications@mg.wp1.openzim.org>",
        "to": f"{recipient_username} <{recipient_email}>",
        "subject": f"Your ZIM File Could Not Be Generated - {zim_title}",
        "text": text,
        "html": html_content,
    }

    return _send_email(email_data)


def _send_email(email_data):
    settings = get_settings()
    try:
        response = requests.post(
            settings.MAILGUN_URL,
            auth=("api", settings.MAILGUN_API_KEY),
            data=email_data,
            timeout=30,
        )

        if response.status_code == 200:
            return True
        else:
            logger.error(
                f"Failed to send email. Status: {response.status_code}, Response: {response.text}"
            )
            return False

    except Exception as e:
        logger.exception("Error sending email")
        return False


def respond_to_zim_task_completed(wp10db, zim_file: ZimTask, zim_schedule: ZimSchedule):
    """Handles a completed ZIM task by decrementing generations and notifying the user."""
    zim_schedules.decrement_remaining_generations(wp10db, zim_schedule.s_id)
    if (
        zim_schedule.s_email is not None
        and zim_schedule.s_email_confirmation_token is None
    ):
        notify_user_for_scheduled_zim(wp10db, zim_file, zim_schedule)


def notify_user_for_scheduled_zim(wp10db, zim_file: ZimTask, zim_schedule: ZimSchedule):
    """Notifies the user when a scheduled ZIM file is ready."""
    zimfile_url = zimfarm.zim_file_url_for_task_id(zim_file.z_task_id)

    next_generation_months = None
    if (
        zim_schedule.s_remaining_generations
        and zim_schedule.s_remaining_generations > 0
    ):
        next_generation_months = zim_schedule.s_interval

    send_zim_ready_email(
        download_url=zimfile_url,
        next_generation_months=next_generation_months,
        **_schedule_email_details(wp10db, zim_schedule),
    )


def notify_user_for_failed_scheduled_zim(
    wp10db, zim_schedule: ZimSchedule, schedule_ended: bool
):
    """Notifies the user when a scheduled ZIM file could not be generated."""
    if (
        zim_schedule.s_email is None
        or zim_schedule.s_email_confirmation_token is not None
    ):
        return

    send_zim_failed_email(
        schedule_ended=schedule_ended,
        **_schedule_email_details(wp10db, zim_schedule),
    )


def respond_to_scheduled_zim_job_failed(job, connection, type, value, traceback):
    """
    RQ failure callback for scheduled ZIM jobs. RQ doesn't repeat a failed job,
    so the failure ends the schedule.
    """
    _, zim_schedule_id = job.args
    wp10db = wp10_connect()
    try:
        zim_schedule = zim_schedules.get_zim_schedule(wp10db, zim_schedule_id)
        if zim_schedule is None:
            return
        notify_user_for_failed_scheduled_zim(wp10db, zim_schedule, schedule_ended=True)
    finally:
        wp10db.close()


def _schedule_email_details(wp10db, zim_schedule: ZimSchedule):
    recipient_username = zim_schedules.get_username_by_zim_schedule_id(
        wp10db, zim_schedule.s_id
    )
    zim_title = (
        zim_schedule.s_title.decode("utf-8")
        if zim_schedule.s_title
        else "Your ZIM File"
    )

    settings = get_settings()
    manage_schedule_url = None
    if settings.CLIENT_HOMEPAGE:
        builder_id = zim_schedule.s_builder_id.decode("utf-8")
        manage_schedule_url = f"{settings.CLIENT_HOMEPAGE}selections/{builder_id}/zim"

    api_url = settings.CLIENT_API_URL.rstrip("/")
    token = zim_schedules.generate_notification_unsubscribe_token(zim_schedule)
    unsubscribe_url = f"{api_url}/v1/zim/unsubscribe-notification?token={token}"

    return {
        "recipient_username": recipient_username,
        "recipient_email": zim_schedule.s_email.decode("utf-8"),
        "zim_title": zim_title,
        "manage_schedule_url": manage_schedule_url,
        "unsubscribe_url": unsubscribe_url,
    }
