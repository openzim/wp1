from typing import Any


class Wp1Error(Exception):
    pass


class Wp1SelectionError(Wp1Error):
    def __init__(self, *args: Any, extra: dict[str, Any] | None = None):
        super().__init__(*args)
        self.extra = extra or {}


class Wp1RetryableSelectionError(Wp1SelectionError):
    pass


class Wp1FatalSelectionError(Wp1SelectionError):
    pass


class Wp1MetaSelectionError(Wp1SelectionError):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        reason: str,
        action: str,
        **details: str | None,
    ):
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.action = action
        self.details = {
            key: value for key, value in details.items() if value is not None
        }


class Wp1RetryableMetaSelectionError(Wp1MetaSelectionError, Wp1RetryableSelectionError):
    pass


class Wp1FatalMetaSelectionError(Wp1MetaSelectionError, Wp1FatalSelectionError):
    pass


class Wp1MetaBuilderProcessError(Wp1SelectionError):
    def __init__(self, failures: list[tuple[dict[str, Any], Wp1SelectionError]]):
        super().__init__("One or more referenced selections failed")
        self.failures = failures

    @property
    def has_fatal_errors(self) -> bool:
        return any(
            isinstance(error, Wp1FatalSelectionError)
            for _reference, error in self.failures
        )

    def to_user_messages(self) -> list[dict[str, Any]]:
        messages = []
        for reference, error in self.failures:
            message = str(error)
            data = {
                "builder_id": reference["id"],
                "builder_name": reference["name"],
                "builder_model": reference["model"],
                "message": message,
                "reason": message,
                "status": (
                    "FAILED"
                    if isinstance(error, Wp1FatalSelectionError)
                    else "CAN_RETRY"
                ),
            }
            if isinstance(error, Wp1MetaSelectionError):
                data.update(
                    {
                        "code": error.code,
                        "reason": error.reason,
                        "action": error.action,
                    }
                )
                data.update(error.details)
            messages.append(data)
        return messages


class ZimFarmError(Wp1Error):
    pass


class InvalidZimTitleError(ZimFarmError):
    pass


class InvalidZimDescriptionError(ZimFarmError):
    pass


class InvalidZimLongDescriptionError(ZimFarmError):
    pass


class InvalidZimFlavourError(ZimFarmError):
    pass


class ZimFarmTooManyArticlesError(ZimFarmError):

    def user_message(self):
        return str(self)


class ObjectNotFoundError(Wp1Error):
    pass


class UserNotAuthorizedError(Wp1Error):
    pass


class Wp1ScoreProcessingError(Wp1Error):
    pass
