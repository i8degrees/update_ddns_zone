# utils namespace

from parse_boolean import parse_boolean
from env import *
from logging import *
from utils import *
from AppConfig import AppConfig

# ?? Attempt to relocate dotenv env object here?

def main():
    # utils exports
    return [
        # parse_boolean.py
        parse_boolean,
        # env.py
        get_env,
        get_env_bool,
        #set_env,
        # logging.py
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
    ]

