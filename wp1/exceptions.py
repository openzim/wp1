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


class ObjectNotFoundError(Wp1Error):
  pass


class UserNotAuthorizedError(Wp1Error):
  pass
