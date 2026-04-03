import logging
import urllib.parse
import uuid
from typing import cast, Any
from datetime import datetime, UTC, timedelta

import regex
import requests
from requests.auth import HTTPBasicAuth

import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
import wp1.logic.zim_schedules as logic_zim_schedules
from wp1 import constants
from wp1.constants import WP1_USER_AGENT
from wp1.credentials import CREDENTIALS, ENV
from wp1.exceptions import (
    InvalidZimDescriptionError,
    InvalidZimLongDescriptionError,
    InvalidZimTitleError,
    ObjectNotFoundError,
    ZimFarmError,
    ZimFarmTooManyArticlesError,
)
from wp1.logic import util
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection
from wp1.models.wp10.zim_schedule import ZimSchedule

REDIS_AUTH_KEY = "zimfarm.auth"

# ZIM metadata limits as per https://wiki.openzim.org/wiki/Metadata
ZIM_TITLE_MAX_LENGTH = 30
ZIM_DESCRIPTION_MAX_LENGTH = 80
ZIM_LONG_DESCRIPTION_MAX_LENGTH = 4000

logger = logging.getLogger(__name__)

# The maximum number of articles that a Selection can contain if the user
# wishes to create a ZIM file for it. For Selections with more than this
# number, we perform validation in the frontend, as well as the API layer.
MAX_ZIMFARM_ARTICLE_COUNT = 50_000


def store_zimfarm_token(redis, data):
    redis.hset(REDIS_AUTH_KEY, mapping=data)


def getnow():
    """naive UTC now"""
    return datetime.now(UTC).replace(tzinfo=None)


class ZimfarmClientTokenProvider:
    """Client to generate access tokens to authenticate with Zimfarm API"""

    def __init__(self):
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: datetime = datetime.fromtimestamp(0, UTC).replace(tzinfo=None)
        self._zimfarm_creds: dict[str, Any] = CREDENTIALS[ENV].get("ZIMFARM", {})

    def _validate_creds(self):
        if self._zimfarm_creds.get("auth_mode", "local") == "local":
            if not (
                self._zimfarm_creds.get("user") and self._zimfarm_creds.get("password")
            ):
                raise ZimFarmError(
                    "user and password must be set in Zimfarm site credentials "
                    "when auth mode is 'local' "
                )
        elif self._zimfarm_creds.get("auth_mode") == "oauth":
            if not (
                self._zimfarm_creds.get("oauth_issuer")
                and self._zimfarm_creds.get("oauth_client_id")
                and self._zimfarm_creds.get("oauth_client_secret")
                and self._zimfarm_creds.get("oauth_audience_id")
            ):
                raise ZimFarmError(
                    "oauth_client_secret, oauth_client_id and oauth_audience_id must be set "
                    "in Zimfarm site credentials when auth mode is 'oauth'"
                )
        else:
            raise ZimFarmError(
                f"Unknown auth mode {self._zimfarm_creds.get('auth_mode')}. "
                "Allowed values are 'local' and 'oauth'."
            )

    def _generate_oauth_access_token(self) -> None:
        """Generate oauth access token and update expires_at."""

        logger.debug(
            "Requesting auth token from %s with oauth credentials",
            self._zimfarm_creds.get("oauth_issuer"),
        )
        response = requests.post(
            f"{self._zimfarm_creds.get('oauth_issuer')}/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "audience": self._zimfarm_creds.get("oauth_audience_id"),
            },
            auth=HTTPBasicAuth(
                self._zimfarm_creds.get("oauth_client_id"),
                self._zimfarm_creds.get("oauth_client_secret"),
            ),
            timeout=self._zimfarm_creds.get("requests_timeout", 30),
            headers={"User-Agent": WP1_USER_AGENT},
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(response.text)
            raise ZimFarmError("Error getting authentication token for Zimfarm") from e

        payload = response.json()
        self._access_token = cast(str, payload["access_token"])
        self._expires_at = getnow() + timedelta(seconds=payload["expires_in"])

    def _generate_local_access_token(self) -> None:
        if self._refresh_token:
            logger.debug(
                "Requesting access_token from %s using refresh_token", get_zimfarm_url()
            )
            response = requests.post(
                f"{get_zimfarm_url()}/auth/refresh",
                json={
                    "refresh_token": self._refresh_token,
                },
                timeout=self._zimfarm_creds.get("requests_timeout", 30),
                headers={"User-Agent": WP1_USER_AGENT},
            )
        else:
            logger.debug(
                "Requesting auth token from %s with username/password",
                get_zimfarm_url(),
            )
            response = requests.post(
                f"{get_zimfarm_url()}/auth/authorize",
                json={
                    "username": self._zimfarm_creds.get("user"),
                    "password": self._zimfarm_creds.get("password"),
                },
                timeout=self._zimfarm_creds.get("requests_timeout", 30),
                headers={"User-Agent": WP1_USER_AGENT},
            )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(response.text)
            raise ZimFarmError("Error getting authentication token for Zimfarm") from e

        payload = response.json()
        self._access_token = cast(str, payload["access_token"])
        self._refresh_token = cast(str, payload["refresh_token"])
        self._expires_at = datetime.fromisoformat(payload["expires_time"]).replace(
            tzinfo=None
        )

    def get_access_token(self, redis) -> str:
        """Retrieve or generate access token depending on if token has expired."""
        self._validate_creds()

        data = redis.hgetall(REDIS_AUTH_KEY)
        if data is not None:
            self._access_token = data.get("access_token")
            self._refresh_token = data.get("refresh_token")
            if data.get("expires_at"):
                self._expires_at = datetime.fromisoformat(data["expires_at"]).replace(
                    tzinfo=None
                )

        now = getnow()
        if self._access_token is None or now >= (
            self._expires_at
            - timedelta(seconds=self._zimfarm_creds.get("token_renewal_window", 300))
        ):
            logger.debug("Refreshing Zimfarm acess token")
            if self._zimfarm_creds.get("auth_mode") == "oauth":
                self._generate_oauth_access_token()
            elif self._zimfarm_creds.get("auth_mode") == "local":
                self._generate_local_access_token()

            if self._access_token:
                store_zimfarm_token(
                    redis,
                    {
                        "access_token": self._access_token,
                        "refresh_token": self._refresh_token or "",
                        "expires_at": self._expires_at.isoformat(),
                    },
                )

        if self._access_token is None:
            raise ZimFarmError("Failed to generate access token.")
        return self._access_token


zimfarm_token_provider = ZimfarmClientTokenProvider()


def get_zimfarm_url():
    url = CREDENTIALS[ENV].get("ZIMFARM", {}).get("url")
    if url is None:
        raise ZimFarmError(
            'CREDENTIALS did not contain ["ZIMFARM"]["url"], environment = %s' % ENV
        )
    return url


def get_webhook_url():
    token = CREDENTIALS[ENV].get("ZIMFARM", {}).get("hook_token")
    if token is None:
        return None

    base_url = CREDENTIALS[ENV].get("CLIENT_URL", {}).get("backend")
    if base_url is None:
        return None

    return "%s/v1/builders/zim/status?token=%s" % (base_url, urllib.parse.quote(token))


def nb_grapheme_for(value: str) -> int:
    """Number of graphemes (visually perceived characters) in a given string"""
    return len(regex.findall(r"\X", value))


def _validate_zim_metadata(title, description, long_description):
    """Validate ZIM metadata fields against length limits."""
    if title is None or title.strip() == "":
        raise InvalidZimTitleError("Title is required.")

    if description is None or description.strip() == "":
        raise InvalidZimDescriptionError("Description is required.")

    if title and nb_grapheme_for(title) > ZIM_TITLE_MAX_LENGTH:
        raise InvalidZimTitleError(
            f"Title exceeds maximum length: {ZIM_TITLE_MAX_LENGTH} graphemes."
        )

    if description and nb_grapheme_for(description) > ZIM_DESCRIPTION_MAX_LENGTH:
        raise InvalidZimDescriptionError(
            f"Description exceeds maximum length: {ZIM_DESCRIPTION_MAX_LENGTH} graphemes."
        )

    if (
        long_description
        and nb_grapheme_for(long_description) > ZIM_LONG_DESCRIPTION_MAX_LENGTH
    ):
        raise InvalidZimLongDescriptionError(
            f"Long description exceeds maximum length: {ZIM_LONG_DESCRIPTION_MAX_LENGTH} graphemes."
        )

    if long_description and nb_grapheme_for(long_description) < nb_grapheme_for(
        description
    ):
        raise InvalidZimLongDescriptionError(
            "Long description must be longer than the description."
        )

    if long_description and long_description == description:
        raise InvalidZimLongDescriptionError(
            "Long description must be different from the description."
        )


def get_zimfarm_schedule_name(builder_id: str) -> str:
    """Generate a unique schedule name for the ZIM file based on builder"""
    if not builder_id:
        raise ValueError("Builder ID cannot be None")
    parts = builder_id.split("-")
    # Use last two parts of the UUIDv4 for more uniqueness
    short_id = "".join(parts[-2:])
    return f"wp1_selection_{short_id}"


def get_zim_filename_prefix(builder: Builder, selection: Selection) -> str:
    """Generate a filename prefix for the ZIM file based on builder and selection."""
    if builder is None or selection is None:
        raise ValueError("Given builder or selection was None")

    selection_id_frag = selection.s_id.decode("utf-8").split("-")[-1]
    builder_name = builder.b_name.decode("utf-8")
    return f"{util.safe_name(builder_name)}-{selection_id_frag}"


def _get_params(
    builder: Builder,
    selection: Selection,
    title: str,
    description: str,
    long_description: str,
) -> dict:
    if builder is None:
        raise ValueError("Given builder was None: %r" % builder)

    project = builder.b_project.decode("utf-8")

    image = CREDENTIALS[ENV].get("ZIMFARM", {}).get("image")
    if image is None:
        image = "ghcr.io/openzim/mwoffliner:latest"
        logger.warning(
            'No ZIMFARM["image"] found in credentials, using latest (%s)', image
        )
    image_name, image_tag = image.split(":")

    config = {
        "warehouse_path": "/wikipedia",
        "image": {
            "name": image_name,
            "tag": image_tag,
        },
        "resources": logic_selection.get_resource_profile(selection),
        "platform": "wikimedia",
        "monitor": False,
        "offliner": {
            "offliner_id": "mwoffliner",
            "mwUrl": "https://%s/" % project,
            "adminEmail": "contact+wp1@kiwix.org",
            "forceRender": "ActionParse",
            "articleList": logic_builder.latest_zimfarm_url_for(
                builder.b_id.decode("utf-8"), selection.s_content_type.decode("utf-8")
            ),
            "customZimTitle": title,
            "customZimDescription": description,
            "customZimLongDescription": (
                long_description
                if long_description
                else f"ZIM file created from a WP1 Selection. {description}"
            ),
            "filenamePrefix": get_zim_filename_prefix(builder, selection),
        },
    }
    cache_url = CREDENTIALS[ENV].get("ZIMFARM", {}).get("cache_url")
    if cache_url is not None:
        config["offliner"]["optimisationCacheUrl"] = cache_url
    else:
        logger.warning(
            "No cache_url found in credentials, skipping "
            "optimisationCacheUrl URL for zimfarm request"
        )

    version = CREDENTIALS[ENV].get("ZIMFARM", {}).get("definition_version", image_tag)

    webhook_url = get_webhook_url()

    return {
        "name": get_zimfarm_schedule_name(builder.b_id.decode("utf-8")),
        "language": "eng",
        "category": "wikipedia",
        "context": "wikimedia",
        "periodicity": "manually",
        "tags": [],
        "enabled": True,
        "notification": {
            "ended": {
                "webhook": [webhook_url] if webhook_url else None,
            },
        },
        "config": config,
        "version": version,
    }


def _get_zimfarm_headers(token):
    return {"Authorization": "Bearer %s" % token, "User-Agent": WP1_USER_AGENT}


def zimfarm_schedule_exists(redis, builder_id: str) -> bool:
    """Checks if a ZimSchedule exists in the zimfarm"""
    token = zimfarm_token_provider.get_access_token(redis)
    base_url = get_zimfarm_url()
    headers = _get_zimfarm_headers(token)

    r = requests.get(
        "%s/schedules/%s" % (base_url, get_zimfarm_schedule_name(builder_id)),
        headers=headers,
    )
    # 404 means the schedule doesn't exist, which is not an error
    if r.status_code == 404:
        return False

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.exception(r.text)
        raise ZimFarmError("Error checking schedule existence") from e

    return r.status_code == 200


def find_existing_schedule_in_db(wp10db, builder_b_id):
    """
    Returns an existing schedule.
    """
    schedules = logic_zim_schedules.list_zim_schedules_for_builder(wp10db, builder_b_id)
    for schedule in schedules:
        if (
            schedule.s_remaining_generations == 0
            or schedule.s_remaining_generations is None
        ):  # Look for a schedule with no remaining generations
            return schedule


def create_or_update_zimfarm_schedule(
    redis, wp10db, builder, title, description, long_description
):
    """
    Requests a ZIM file schedule from the Zimfarm for the given builder.
    """
    token = zimfarm_token_provider.get_access_token(redis)

    if builder is None:
        raise ObjectNotFoundError("Cannot schedule for None builder")

    _validate_zim_metadata(title, description, long_description)

    selection = logic_builder.latest_selection_for(
        wp10db, builder.b_id, "text/tab-separated-values"
    )
    article_count = selection.s_article_count
    if article_count is None or article_count > MAX_ZIMFARM_ARTICLE_COUNT:
        raise ZimFarmTooManyArticlesError(
            "Cannot create ZIM file for selection with %s articles, max is %s"
            % (
                article_count if article_count is not None else "UNKNOWN number of",
                MAX_ZIMFARM_ARTICLE_COUNT,
            )
        )

    params = _get_params(builder, selection, title, description, long_description)
    base_url = get_zimfarm_url()
    headers = _get_zimfarm_headers(token)

    builder_id = builder.b_id.decode("utf-8")

    logger.info(
        "Creating or Updating zimfarm schedule for ZIM for builder id=%s", builder_id
    )
    try:
        existing_zim_schedule = find_existing_schedule_in_db(wp10db, builder.b_id)
        if existing_zim_schedule and zimfarm_schedule_exists(redis, builder_id):
            schedule_name = get_zimfarm_schedule_name(builder_id)
            r = requests.patch(
                "%s/schedules/%s" % (base_url, schedule_name),
                headers=headers,
                json=params,
            )
            r.raise_for_status()
            zim_schedule = existing_zim_schedule
            zim_schedule.s_title = title.encode("utf-8")
            zim_schedule.s_description = description.encode("utf-8")
            zim_schedule.s_long_description = (
                long_description.encode("utf-8") if long_description else None
            )
            zim_schedule.s_remaining_generations = None
            logic_zim_schedules.update_zim_schedule(wp10db, zim_schedule)
            zim_schedule_id_to_set = zim_schedule.s_id.decode("utf-8")
        else:
            r = requests.post("%s/schedules" % base_url, headers=headers, json=params)
            r.raise_for_status()
            zim_schedule_id = str(uuid.uuid4())
            zim_schedule = ZimSchedule(
                s_id=zim_schedule_id.encode("utf-8"),
                s_builder_id=builder.b_id,
                s_last_updated_at=datetime.now(UTC)
                .strftime(constants.TS_FORMAT_WP10)
                .encode("utf-8"),
                s_title=title.encode("utf-8"),
                s_description=description.encode("utf-8"),
                s_long_description=(
                    long_description.encode("utf-8") if long_description else None
                ),
            )
            logic_zim_schedules.insert_zim_schedule(wp10db, zim_schedule)
            zim_schedule_id_to_set = zim_schedule_id
    except requests.exceptions.HTTPError as e:
        logger.exception(r.text)
        raise ZimFarmError(
            "Error creating or updating schedule for ZIM file creation"
        ) from e

    logic_zim_schedules.set_zim_schedule_id_to_zim_task_by_selection(
        wp10db, selection.s_id, zim_schedule_id_to_set
    )
    wp10db.commit()

    return zim_schedule


def request_zimfarm_task(redis, wp10db, builder):
    """
    Requests a ZIM file task from the Zimfarm for the given builder.
    """
    token = zimfarm_token_provider.get_access_token(redis)
    if builder is None:
        raise ObjectNotFoundError("Cannot schedule for None builder")

    selection = logic_builder.latest_selection_for(
        wp10db, builder.b_id, "text/tab-separated-values"
    )
    article_count = selection.s_article_count
    if article_count is None or article_count > MAX_ZIMFARM_ARTICLE_COUNT:
        raise ZimFarmTooManyArticlesError(
            "Cannot create ZIM file for selection with %s articles, max is %s"
            % (
                article_count if article_count is not None else "UNKNOWN number of",
                MAX_ZIMFARM_ARTICLE_COUNT,
            )
        )

    base_url = get_zimfarm_url()
    headers = _get_zimfarm_headers(token)

    schedule_name = get_zimfarm_schedule_name(builder.b_id.decode("utf-8"))
    logger.info("Creating ZIM task for builder id=%s", builder.b_id.decode("utf-8"))
    r = requests.post(
        "%s/requested-tasks" % base_url,
        headers=headers,
        json={"schedule_names": [schedule_name]},
    )
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.exception(r.text)
        raise ZimFarmError("Error requesting task for ZIM file creation") from e

    data = r.json()
    requested = data.get("requested")
    task_id = requested[0] if requested else None
    logger.info(
        "Found task id=%s for builder id=%s", task_id, builder.b_id.decode("utf-8")
    )
    if task_id is None:
        raise ZimFarmError("Did not get scheduled task id")

    return task_id


def _get_task_by_id(task_id):
    if isinstance(task_id, bytes):
        task_id = task_id.decode("utf-8")
    base_url = get_zimfarm_url()

    r = requests.get("%s/tasks/%s" % (base_url, task_id))
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        logger.exception(r.text)
        return None

    return r.json()


def zim_file_url_for_task_id(task_id):
    data = _get_task_by_id(task_id)

    if data is None:
        return None

    files = data.get("files", {})
    name = None
    for _, value in files.items():
        name = value.get("name")
        break

    if name is None:
        raise ZimFarmError(
            "Could not find filename for ZIM file, task_id = %s" % task_id
        )

    warehouse_path = data.get("config", {}).get("warehouse_path")
    if warehouse_path is None:
        raise ZimFarmError(
            "Could not get warehouse path for ZIM file, task_id = %s" % task_id
        )

    base_url = CREDENTIALS[ENV].get("ZIMFARM", {}).get("s3_url")
    if base_url is None:
        raise ZimFarmError(
            'Configuration error, could not find ZIMFARM["s3_url"] in credentials'
        )

    return f"{base_url}{warehouse_path}/{name}"


def cancel_zim_by_task_id(redis, task_id):
    if isinstance(task_id, bytes):
        task_id = task_id.decode("utf-8")

    token = zimfarm_token_provider.get_access_token(redis)
    base_url = get_zimfarm_url()
    headers = _get_zimfarm_headers(token)

    logger.info("Deleting requested task_id=%s", task_id)
    r = requests.delete("%s/requested-tasks/%s" % (base_url, task_id), headers=headers)

    try:
        r.raise_for_status()
        return
    except requests.exceptions.HTTPError as e:
        if r.status_code != 404:
            raise ZimFarmError(
                "Error attempting to delete requested task id=%s" % task_id
            ) from e

    logger.info("Task was no longer requested, cancelling (task_id=%s)", task_id)
    r = requests.post("%s/tasks/%s/cancel" % (base_url, task_id), headers=headers)

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        raise ZimFarmError("Task could not be deleted/canceled (task_id=%s)" % task_id)


def delete_zimfarm_schedule_by_builder_id(redis, builder_id):
    """
    Deletes a ZIM schedule from the Zimfarm for the given builder_id.
    """
    if isinstance(builder_id, bytes):
        builder_id = builder_id.decode("utf-8")

    token = zimfarm_token_provider.get_access_token(redis)

    base_url = get_zimfarm_url()
    headers = _get_zimfarm_headers(token)
    schedule_name = get_zimfarm_schedule_name(builder_id)

    logger.info(
        "Deleting zimfarm schedule=%s for builder_id=%s", schedule_name, builder_id
    )
    r = requests.delete("%s/schedules/%s" % (base_url, schedule_name), headers=headers)

    try:
        r.raise_for_status()
        logger.info("Successfully deleted zimfarm schedule=%s", schedule_name)
    except requests.exceptions.HTTPError as e:
        if r.status_code == 404:
            # Schedule doesn't exist, which is not an error for deletion
            logger.info(
                "Zimfarm schedule=%s not found (already deleted or never existed)",
                schedule_name,
            )
            return
        else:
            logger.exception(r.text)
            raise ZimFarmError(
                "Error deleting zimfarm schedule=%s" % schedule_name
            ) from e
