class Wp1Error(Exception):
  pass


class Wp1SelectionError(Wp1Error):
  pass


class Wp1RetryableSelectionError(Wp1SelectionError):
  pass


class Wp1FatalSelectionError(Wp1SelectionError):
  pass


class ZimFarmError(Wp1Error):
  pass


class InvalidZimTitleError(ZimFarmError):
  pass


class InvalidZimDescriptionError(ZimFarmError):
  pass


class InvalidZimLongDescriptionError(ZimFarmError):
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
