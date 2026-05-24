from typing import Any

import attr
import secrets
from dateutil.relativedelta import relativedelta
from pymysql.connections import Connection
from redis import Redis

import wp1.queues as queues

from wp1.constants import TS_FORMAT_WP10, SECONDS_PER_MONTH
from wp1.credentials import CREDENTIALS, ENV
from wp1.timestamp import utcnow
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.web.emails_confirmation import send_zim_email_confirmation


def insert_zim_schedule(wp10db: Connection, zim_schedule: ZimSchedule) -> None:
    """Inserts a ZimSchedule into the zim_schedules table"""
    with wp10db.cursor() as cursor:
        cursor.execute(
            """INSERT INTO zim_schedules
         (s_id, s_builder_id, s_rq_job_id, s_last_updated_at,
          s_interval, s_remaining_generations, s_email, s_title, s_description,
          s_long_description, s_email_confirmation_token, s_flavour)
         VALUES
         (%(s_id)s, %(s_builder_id)s,  %(s_rq_job_id)s,
          %(s_last_updated_at)s, %(s_interval)s, %(s_remaining_generations)s,
          %(s_email)s, %(s_title)s, %(s_description)s, %(s_long_description)s,
          %(s_email_confirmation_token)s, %(s_flavour)s)
      """,
            attr.asdict(zim_schedule),
        )
    wp10db.commit()


def update_zim_schedule(wp10db: Connection, zim_schedule: ZimSchedule) -> bool:
    """Updates a ZimSchedule record based on the model state. Returns True if updated."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            """UPDATE zim_schedules SET
         s_last_updated_at = %(s_last_updated_at)s,
         s_interval = %(s_interval)s,
         s_remaining_generations = %(s_remaining_generations)s,
         s_email = %(s_email)s,
         s_title = %(s_title)s,
         s_description = %(s_description)s,
         s_long_description = %(s_long_description)s,
         s_email_confirmation_token = %(s_email_confirmation_token)s,
         s_flavour = %(s_flavour)s
         WHERE s_id = %(s_id)s
      """,
            attr.asdict(zim_schedule),
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def get_zim_schedule(wp10db: Connection, schedule_id: bytes) -> ZimSchedule | None:
    """Retrieves a ZimSchedule by its s_id. Returns a ZimSchedule or None."""
    with wp10db.cursor() as cursor:
        cursor.execute("SELECT * FROM zim_schedules WHERE s_id = %s", (schedule_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return ZimSchedule(**row)


def get_zim_schedule_by_zim_file_id(
    wp10db: Connection, z_id: int
) -> ZimSchedule | None:
    """Retrieves a ZimSchedule by its associated zim_file_id."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            """
      SELECT zs.* FROM zim_schedules zs
      JOIN zim_tasks zf ON zs.s_id = zf.z_zim_schedule_id
      WHERE zf.z_id = %s
      """,
            (z_id,),
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimSchedule(**row)


def list_zim_schedules_for_builder(
    wp10db: Connection, builder_id: str | bytes
) -> list[ZimSchedule]:
    """Lists all ZimSchedule entries for a given builder_id."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM zim_schedules WHERE s_builder_id = %s", (builder_id,)
        )
        rows = cursor.fetchall()
    return [ZimSchedule(**row) for row in rows]


def find_active_recurring_schedule_for_builder(
    wp10db: Connection, builder_id: str | bytes
) -> ZimSchedule | None:
    """Returns an active recurring schedule for a builder (remaining_generations > 0)."""
    schedules = list_zim_schedules_for_builder(wp10db, builder_id)
    for schedule in schedules:
        if (
            schedule.s_remaining_generations is not None
            and schedule.s_remaining_generations > 0
        ):
            return schedule
    return None


def delete_zim_schedule(redis: Redis, wp10db: Connection, schedule_id: bytes) -> bool:
    """Deletes a ZIM schedule by canceling the RQ job and removing the database record."""
    schedule = get_zim_schedule(wp10db, schedule_id)
    if not schedule:
        return False

    # Cancel the scheduled RQ job if it exists
    if schedule.s_rq_job_id:
        queues.cancel_scheduled_job(redis, schedule.s_rq_job_id.decode("utf-8"))

    # Delete the schedule from the database
    with wp10db.cursor() as cursor:
        cursor.execute("DELETE FROM zim_schedules WHERE s_id = %s", (schedule_id,))
        deleted = bool(cursor.rowcount)
    wp10db.commit()

    return deleted


def decrement_remaining_generations(wp10db: Connection, schedule_id: bytes) -> bool:
    """Decrements s_remaining_generations by 1 for the given schedule, not going below 0. Also updates s_last_updated_at. Returns True if updated."""
    updated_at = utcnow().strftime(TS_FORMAT_WP10).encode("utf-8")
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT s_remaining_generations FROM zim_schedules WHERE s_id = %s",
            (schedule_id,),
        )
        row = cursor.fetchone()
        if (
            not row
            or not row["s_remaining_generations"]
            or row["s_remaining_generations"] <= 0
        ):
            return False
        new_value = row["s_remaining_generations"] - 1
        cursor.execute(
            "UPDATE zim_schedules SET s_remaining_generations = %s, s_last_updated_at = %s WHERE s_id = %s",
            (new_value, updated_at, schedule_id),
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def get_scheduled_zimfarm_task_from_taskid(
    wp10db: Connection, task_id: str | bytes
) -> ZimSchedule | None:
    """Checks if a task_id is scheduled in zim_schedules. Returns the ZimSchedule if found, else None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT zs.* FROM zim_schedules zs JOIN zim_tasks zf ON zs.s_id = zf.z_zim_schedule_id WHERE zf.z_task_id = %s",
            (task_id,),
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimSchedule(**row)


def get_username_by_zim_schedule_id(
    wp10db: Connection, schedule_id: bytes
) -> str | None:
    """Retrieves the username associated with a ZimSchedule by its ID. Returns the username or None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT u.u_username FROM zim_schedules zs "
            "JOIN builders b ON zs.s_builder_id = b.b_id "
            "JOIN users u ON b.b_user_id = u.u_id "
            "WHERE zs.s_id = %s",
            (schedule_id,),
        )
        row = cursor.fetchone()
    if not row:
        return None
    return row["u_username"].decode("utf-8") if row["u_username"] else None


def set_zim_schedule_id_to_zim_task_by_selection(
    wp10db: Connection, selection_id: bytes, zim_schedule_id: bytes
) -> bool:
    """Sets the z_zim_schedule_id field in zim_tasks to the given the selection_id."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "UPDATE zim_tasks SET z_zim_schedule_id = %s WHERE z_selection_id = %s",
            (zim_schedule_id, selection_id),
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def has_email_been_confirmed(wp10db: Connection, email: bytes) -> bool:
    """Checks if an email address has been previously confirmed in any zim_schedule.
    Returns True if the email exists with no confirmation token (confirmed), False otherwise.
    """
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM zim_schedules WHERE s_email = %s AND s_email_confirmation_token IS NULL LIMIT 1",
            (email,),
        )
        return cursor.fetchone() is not None


def confirm_email_subscription(
    wp10db: Connection, token: str | bytes, email: str | bytes
) -> bool:
    """Confirms email subscription by removing tokens for all schedules with the given email.
    First validates that the token exists for this email. Returns True if found and confirmed.
    """
    with wp10db.cursor() as cursor:
        # Validate that the token exists for this email
        cursor.execute(
            "SELECT 1 FROM zim_schedules WHERE s_email_confirmation_token = %s AND s_email = %s LIMIT 1",
            (token, email),
        )
        if not cursor.fetchone():
            return False

        # Update all schedules with this email to remove their tokens (confirm them all)
        cursor.execute(
            "UPDATE zim_schedules SET s_email_confirmation_token = NULL WHERE s_email = %s",
            (email,),
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def unsubscribe_email(wp10db: Connection, token: str | bytes) -> bool:
    """Unsubscribes from email notifications by removing email and token. Returns True if found and unsubscribed."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "UPDATE zim_schedules SET s_email = NULL, s_email_confirmation_token = NULL WHERE s_email_confirmation_token = %s",
            (token,),
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def unsubscribe_email_by_schedule_id(wp10db: Connection, schedule_id: bytes) -> bool:
    """Unsubscribes from email notifications by removing email from a schedule. Returns True if found and unsubscribed."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "UPDATE zim_schedules SET s_email = NULL WHERE s_id = %s AND s_email IS NOT NULL",
            (schedule_id,),
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def get_zim_schedule_by_token(
    wp10db: Connection, token: str | bytes
) -> ZimSchedule | None:
    """Retrieves a ZimSchedule by its email confirmation token. Returns a ZimSchedule or None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM zim_schedules WHERE s_email_confirmation_token = %s",
            (token,),
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimSchedule(**row)


def generate_email_confirmation_token() -> bytes:
    """Generates a secure random token for email confirmation."""
    return secrets.token_urlsafe(32).encode("utf-8")


def schedule_future_zimfile_generations(
    redis: Redis,
    wp10db: Connection,
    builder: Builder,
    zim_schedule_id: bytes,
    scheduled_repetitions: dict[str, Any],
) -> str:
    """
    Calculate timing and schedule future ZIM file creations using rq-scheduler, then save the schedule to the database.
    """

    required_keys = {"repetition_period_in_months", "number_of_repetitions"}
    has_min_required_keys = required_keys <= scheduled_repetitions.keys()
    if not isinstance(scheduled_repetitions, dict) or not has_min_required_keys:
        raise ValueError(
            f"scheduled_repetitions must be a dict containing {required_keys}"
        )

    period_months = scheduled_repetitions["repetition_period_in_months"]
    interval_seconds = period_months * SECONDS_PER_MONTH
    first_future_run = utcnow() + relativedelta(seconds=interval_seconds)
    total_repetitions = scheduled_repetitions["number_of_repetitions"]
    email = scheduled_repetitions.get("email")
    email = email.encode("utf-8") if email is not None else None

    job = queues.schedule_recurring_zimfarm_task(
        redis=redis,
        args=[builder, zim_schedule_id],
        scheduled_time=first_future_run,
        interval_seconds=interval_seconds,
        repeat_count=total_repetitions
        - 1,  # -1 because the first run is not counted as a repetition
    )

    zim_schedule = get_zim_schedule(wp10db, zim_schedule_id)
    if zim_schedule is None:
        raise ValueError(f"ZimSchedule not found for id={zim_schedule_id!r}")
    zim_schedule.s_remaining_generations = total_repetitions
    zim_schedule.s_interval = period_months
    zim_schedule.s_rq_job_id = job.id.encode("utf-8")
    zim_schedule.s_email = email
    zim_schedule.set_last_updated_at_now()
    if email is not None and not has_email_been_confirmed(wp10db, email):
        # Email not previously confirmed, generate token and send confirmation email
        zim_schedule.s_email_confirmation_token = generate_email_confirmation_token()
        username = get_username_by_zim_schedule_id(wp10db, zim_schedule_id)
        zim_title = (
            zim_schedule.s_title.decode("utf-8")
            if zim_schedule.s_title
            else "Your ZIM File"
        )

        token = zim_schedule.s_email_confirmation_token.decode("utf-8")
        email_confirm_url = CREDENTIALS.get(ENV, {}).get("CLIENT_URL", {}).get("api")
        confirm_url = f"{email_confirm_url}/v1/zim/confirm-email?token={token}"
        unsubscribe_url = f"{email_confirm_url}/v1/zim/unsubscribe-email?token={token}"
        send_zim_email_confirmation(
            recipient_username=username,
            recipient_email=email.decode("utf-8"),
            zim_title=zim_title,
            confirm_url=confirm_url,
            unsubscribe_url=unsubscribe_url,
            repetition_period_months=period_months,
            number_of_repetitions=total_repetitions,
        )

    update_zim_schedule(wp10db, zim_schedule)

    return job.id
