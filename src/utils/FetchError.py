#from .util import strclass_
from .Error import Error

DEFAULT_ERROR_DICT = {
  "status_code": -1,
  "status_message": "",
  "stack": "",
}

""" FetchError class for handling HTTP Status Code response"""
class FetchError(Error):

  def __init__(self, code: int, msg: str, details: dict = {}) -> None:
    super().__init__(code, msg, details)
