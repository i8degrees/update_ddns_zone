# utils namespace

from .parse_boolean import parse_boolean
from .env import *
from logging import *
from utils.util import *
from utils.log_impl import *
from .AppConfig import AppConfig
from .FetchError import FetchError

# ?? Attempt to relocate dotenv env object here?

def main():
    # utils exports; I have no clue as to if this is the proper way of
    # doing this?
    # a) I do not want an executable called utils to be produced.
    # b) I think I should be doing this export in __init__.py instead so that
    # I can treat this as a proper library namespace?
    return [
        # parse_boolean.py
        parse_boolean,
        # env.py
        get_env,
        get_env_bool,
        #set_env,
        # log_impl.py
        message,
        crit,
        error,
        warn,
        verbose,
        log_debug,
        verbose_debug,
        debug_trace,
        # util.py
        update_record,
        delete_record,
        short_hostname,
        canonical_dns_name,
        # AppConfig.py
        AppConfig,
        # FetchError.py
        FetchError,
    ]

