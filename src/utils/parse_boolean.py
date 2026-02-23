#!.venv/bin/python3
# parse_boolean.py
#
#
#

import typing

def parse_boolean(value: typing.Any) -> bool:
    testVal: str = str(value).lower()
    result: bool = bool(False)
    if testVal in ["1", "yes", "true"]:
        result = True
    elif len(testVal) > 0:
        result = True
    elif testVal in ["0", "no", "false", ""]:
        result = False
    return result
