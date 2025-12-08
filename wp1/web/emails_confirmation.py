import requests
import logging

from wp1.credentials import CREDENTIALS, ENV
from wp1.templates import env as jinja_env


logger = logging.getLogger(__name__)


def send_zim_email_confirmation(
    recipient_username,
    recipient_email,
    zim_title,
    confirm_url,
    unsubscribe_url,
    repetition_period_months,
    number_of_repetitions,
):
    """Sends an email confirmation for ZIM file notifications."""

    mailgun_config = CREDENTIALS.get(ENV, {}).get("MAILGUN", {})
    if not mailgun_config or not mailgun_config.get("api_key"):
        logger.warning("Mailgun not configured. Confirmation email not sent.")
        return False

    template = jinja_env.get_template("zim-email-confirmation.html.jinja2")

    context = {
        "user": recipient_username,
        "title": zim_title,
        "user_email": recipient_email,
        "confirm_url": confirm_url,
        "unsubscribe_url": unsubscribe_url,
        "repetition_period_months": repetition_period_months,
        "number_of_repetitions": number_of_repetitions,
    }

    html_content = template.render(**context)

    email_data = {
        "from": "Wikipedia WP 1.0 Project <notifications@mg.wp1.openzim.org>",
        "to": f"{recipient_username} <{recipient_email}>",
        "subject": f"Confirm Email Notifications for ZIM File - {zim_title}",
        "text": f"Hello {recipient_username},\n\nPlease confirm your email address to receive notifications when your ZIM file '{zim_title}' is ready for download.\n\nConfirm: {confirm_url}\n\nDecline: {unsubscribe_url}",
        "html": html_content,
    }

    try:
        response = requests.post(
            mailgun_config["url"],
            auth=("api", mailgun_config["api_key"]),
            data=email_data,
            timeout=30,
        )

        if response.status_code == 200:
            return True
        else:
            logger.error(
                f"Failed to send confirmation email. Status: {response.status_code}, Response: {response.text}"
            )
            return False

    except Exception as e:
        logger.exception("Error sending confirmation email")
        return False
