#!.venv/bin/python3
# logging.py
#
# !! TODO(JEFF): Refactor to utilize the built-in logging module

import os
#from enum import Enum
#import errno
from typing import Final # type: ignore

from .parse_boolean import *
#from env import * # env.py

# !! TODO
#from logging import basicConfig

config = {
    **os.environ
}

config.setdefault("DEBUG", "")
config.setdefault("DEBUG_TRACE", "")
config.setdefault("VERBOSE", "")
config.setdefault("SYSLOG", "")

def message(tag:str, msg: str) -> None:
    if not tag:
        tag = "INFO"
    print(tag, ":", msg)

def crit(tag:str, msg: str) -> None:
    if not tag:
        tag = "CRITICAL"
    print(tag, ":", msg)

def error(tag:str, msg: str) -> None:
    if not tag:
        tag = "ERROR"
    print(tag, ":", msg)

def warn(tag:str, msg: str) -> None:
    if not tag:
        tag = "WARNING"
    print(tag, ":", msg)

def verbose(tag:str, msg: str) -> None:
    if not tag:
        tag = "VERBOSE"
    if parse_boolean(config["VERBOSE"]) == True:
        print(tag, ":", msg)

def log_debug(tag:str, msg: str) -> None:
    if not tag:
        tag = "DEBUG"

    if parse_boolean(config["DEBUG"]) == True:
        print(tag, ":", msg)
    else:
        return

def verbose_debug(tag:str, msg: str) -> None:
    if not tag:
        tag = "DEBUG_VERBOSE"
    if parse_boolean(config["VERBOSE"]) == True and parse_boolean(config["DEBUG"]) == True:
        print(tag, ":", msg)

def debug_trace(tag:str, msg: str) -> None:
    if not tag:
        tag = "DEBUG_TRACE"
    if parse_boolean(config["DEBUG_TRACE"]):
        print(tag, ":", msg)
