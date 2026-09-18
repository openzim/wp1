import flask
import logging

from wp1.web.db import get_db
from wp1.logic import zim_schedules
from wp1.templates import env as jinja_env

logger = logging.getLogger(__name__)

zim_emails = flask.Blueprint("zim_emails", __name__)


def render_error_page(
    title, heading, message, status_code=400, is_success=False, zim_title=None
):
    """Renders a standardized error/success page using the shared template."""
    template = jinja_env.get_template("zim-email-error.html.jinja2")
    html_content = template.render(
        title=title,
        heading=heading,
        message=message,
        is_success=is_success,
        zim_title=zim_title,
    )
    return flask.Response(html_content, status=status_code, mimetype="text/html")


@zim_emails.route("/confirm-email")
def confirm_email():
    """Confirms email subscription for ZIM notifications."""
    token = flask.request.args.get("token")
    if not token:
        return render_error_page(
            title="Invalid Link",
            heading="Invalid Confirmation Link",
            message="This confirmation link is invalid or missing required parameters.",
        )

    wp10db = get_db("wp10db")

    # Get the schedule details before confirming
    schedule = zim_schedules.get_zim_schedule_by_token(wp10db, token.encode("utf-8"))
    if not schedule:
        return render_error_page(
            title="Invalid Token",
            heading="Invalid or Expired Confirmation Link",
            message="This confirmation link is invalid, expired, or has already been used.",
            status_code=404,
        )

    # Confirm the email subscription
    success = zim_schedules.confirm_email_subscription(
        wp10db, token.encode("utf-8"), schedule.s_email
    )

    if success:
        zim_title = (
            schedule.s_title.decode("utf-8") if schedule.s_title else "Your ZIM File"
        )
        return render_error_page(
            title="Email Confirmed",
            heading="Email Confirmed Successfully!",
            message="You will now receive email notifications when your ZIM file generation is completed.",
            status_code=200,
            is_success=True,
            zim_title=zim_title,
        )
    else:
        return render_error_page(
            title="Confirmation Failed",
            heading="Confirmation Failed",
            message="Unable to confirm your email subscription. The link may have already been used or expired.",
        )


@zim_emails.route("/unsubscribe-email")
def unsubscribe_email():
    """Unsubscribes from email notifications for ZIM files."""
    token = flask.request.args.get("token")
    if not token:
        return render_error_page(
            title="Invalid Link",
            heading="Invalid Unsubscribe Link",
            message="This unsubscribe link is invalid or missing required parameters.",
        )

    wp10db = get_db("wp10db")

    # Get the schedule details before unsubscribing
    schedule = zim_schedules.get_zim_schedule_by_token(wp10db, token.encode("utf-8"))
    if not schedule:
        return render_error_page(
            title="Invalid Token",
            heading="Invalid or Expired Unsubscribe Link",
            message="This unsubscribe link is invalid, expired, or has already been used.",
            status_code=404,
        )

    # Unsubscribe from email notifications
    success = zim_schedules.unsubscribe_email(wp10db, token.encode("utf-8"))

    if success:
        zim_title = (
            schedule.s_title.decode("utf-8") if schedule.s_title else "Your ZIM File"
        )
        return render_error_page(
            title="Successfully Unsubscribed",
            heading="Successfully Unsubscribed",
            message="You will no longer receive email notifications for this ZIM file generation.",
            status_code=200,
            is_success=True,
            zim_title=zim_title,
        )
    else:
        return render_error_page(
            title="Unsubscribe Failed",
            heading="Unsubscribe Failed",
            message="Unable to unsubscribe from email notifications. The link may have already been used or expired.",
        )


@zim_emails.route("/unsubscribe-notification")
def unsubscribe_notification():
    """Unsubscribe using a signed capability, without requiring a session."""
    token = flask.request.args.get("token")
    if not token:
        return render_error_page(
            title="Invalid Link",
            heading="Invalid Unsubscribe Link",
            message="This unsubscribe link is invalid or missing required parameters.",
        )

    wp10db = get_db("wp10db")

    if zim_schedules.unsubscribe_notification(wp10db, token):
        return render_error_page(
            title="Successfully Unsubscribed",
            heading="Successfully Unsubscribed",
            message="You will no longer receive email notifications for this ZIM file generation.",
            status_code=200,
            is_success=True,
        )
    else:
        return render_error_page(
            title="Invalid Token",
            heading="Invalid or Already Unsubscribed",
            message="This unsubscribe link is invalid, no longer matches the recipient, or has already been used.",
            status_code=404,
        )
