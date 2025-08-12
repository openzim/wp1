
import requests
import logging

from wp1 import zimfarm
from wp1.credentials import CREDENTIALS, ENV
from wp1.logic import zim_schedules
from wp1.models.wp10.zim_file import ZimTask
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.templates import env as jinja_env


logger = logging.getLogger(__name__)


def send_zim_ready_email(recipient_username,
                         recipient_email,
                         zim_title, download_url,
                         manage_schedule_url=None,
                         unsubscribe_url=None,
                         next_generation_months=None):
    """Sends an email notification when a ZIM file is ready for download."""
    
    mailgun_config = CREDENTIALS.get(ENV, {}).get('MAILGUN', {})
    if not mailgun_config or not mailgun_config.get('api_key'):
        logger.warning("Mailgun not configured. Email not sent.")
        return False
    
    template = jinja_env.get_template('generated-scheduled-zim-email.html.jinja2')
    
    context = {
        'user': recipient_username,
        'title': zim_title,
        'download_url': download_url,
        'manage_schedule_url': manage_schedule_url or '#',
        'unsubscribe_url': unsubscribe_url or '#',
        'block_email': unsubscribe_url or '#',
        'next_generation_months': next_generation_months
    }
    
    html_content = template.render(**context)
    
    email_data = {
        "from": "Wikipedia WP 1.0 Project <notifications@mg.wp1.openzim.org>",
        "to": f"{recipient_username} <{recipient_email}>",
        "subject": f"Your ZIM File is Ready for Download - {zim_title}",
        "text": f"Hello {recipient_username},\n\nYour ZIM file '{zim_title}' is ready for download at {download_url}.",
        "html": html_content
    }
    
    try:
        response = requests.post(
            mailgun_config['url'],
            auth=("api", mailgun_config['api_key']),
            data=email_data,
            timeout=30
        )
        
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Failed to send email. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        logger.exception("Error sending email")
        return False


def respond_to_zim_task_completed(wp10db, zim_file: ZimTask, zim_schedule: ZimSchedule):
    """Handles a completed ZIM task by decrementing generations and notifying the user."""
    zim_schedules.decrement_remaining_generations(wp10db, zim_schedule.s_id)
    notify_user_for_scheduled_zim(wp10db, zim_file, zim_schedule)


def notify_user_for_scheduled_zim(wp10db, zim_file: ZimTask, zim_schedule: ZimSchedule):
    """Notifies the user when a scheduled ZIM file is ready."""
    zimfile_url = zimfarm.zim_file_url_for_task_id(zim_file.z_task_id)
    recipient_email = zim_schedule.s_email.decode('utf-8')
    recipient_username = zim_schedules.get_username_by_zim_schedule_id(wp10db, zim_schedule.s_id)
    zim_title = zim_schedule.s_title.decode('utf-8') if zim_schedule.s_title else 'Your ZIM File'

    next_generation_months = None
    if zim_schedule.s_remaining_generations and zim_schedule.s_remaining_generations > 0:
        next_generation_months = zim_schedule.s_interval
    
    send_zim_ready_email(
        recipient_username=recipient_username,
        recipient_email=recipient_email,
        zim_title=zim_title,
        download_url=zimfile_url,
        next_generation_months=next_generation_months
    )