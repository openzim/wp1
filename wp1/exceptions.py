class Wp1SelectionError(Exception):
  pass


class Wp1RetryableSelectionError(Wp1SelectionError):
  pass


class Wp1FatalSelectionError(Wp1SelectionError):
  pass
