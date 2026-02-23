#!.venv/bin/python3
# env.py
#
#
#

import os
from .parse_boolean import *

def get_env(env_var: str, default_value: str = "") -> str|None:
    result: str|None = None
    if len(default_value) > 0:
        result = os.environ.get(env_var, default_value)
    else:
        result = os.environ.get(env_var)
    return result

# get_env("DEBUG", "True")
# get_env("DEBUG", "1")
# get_env("DNSMASQ_ENABLED", "enabled")
def get_env_bool(env_var: str, default_value: str = "") -> bool:
    result: bool = False
    resultVal: str|None = None
    if len(default_value) > 0:
        resultVal = os.environ.get(env_var, default_value)
    else:
        resultVal = os.environ.get(env_var)
    return parse_boolean(result)

# ?? TODO(JEFF): Verify that this actually modifies the environment outside the
# scope of this script!
def set_env(env_var, value) -> str|None:
    value = os.environ.get(env_var)
    return get_env(env_var)
