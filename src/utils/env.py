#!.venv/bin/python3
# env.py
#
#
#

import os
from .parse_boolean import *

def get_env(env_var: str, default_value: any) -> str|None:
    result = None
    if default_value:
        result = os.environ.get(env_var, default_value)
    else:
        #result = ""
        result = os.environ.get(env_var)
    return result

# get_env("DEBUG", "True")
# get_env("DEBUG", "1")
# get_env("DNSMASQ_ENABLED", "enabled")
def get_env_bool(env_var: str, default_value: str = "") -> bool:
    result: bool = False
    resultVal: str|None = None
    if default_value and len(default_value) > 0:
        resultVal = os.environ.get(env_var, default_value)
    else:
        resultVal = os.environ.get(env_var)
    return parse_boolean(result)
