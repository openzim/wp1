"""
This wrapper class exists so that the current time can be mocked in tests.
"""
from datetime import datetime


def get_current_datetime():
  return datetime.now()
