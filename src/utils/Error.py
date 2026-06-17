
DEFAULT_ERROR_DICT = {
  "status_code": -1,
  "status_message": "",
  "stack": "",
}

class Error:
  def __init__(self, code: int, msg: str, details: dict = {}) -> None:
    self.error = DEFAULT_ERROR_DICT
    self.create(code, msg, details)

  def create(self, code: int, msg: str, details: dict = {}):
    self.set_code(code)
    self.set_message(msg)
    self.set_stack(details)

  def error(self):
    return self.error

  def code(self) -> int:
    return self.error.get("status_code")

  """ Alias method """
  def status_code(self) -> int:
    return self.code()

  def message(self) -> str:
    return self.error.get("status_message")

  """ Alias method """
  def status_message(self) -> str:
    return self.message()

  def stack(self) -> dict:
    return self.error.get("stack")

  """ Alias method """
  def details(self) -> dict:
    return self.stack()

  def set_code(self, code: int) -> None:
    self.error["status_code"] = code

  def set_message(self, msg: str) -> None:
    self.error["status_message"] = msg

  def set_stack(self, details: dict) -> None:
    self.error["stack"] = details
