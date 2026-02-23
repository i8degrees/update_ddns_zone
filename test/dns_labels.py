#!.venv/bin/python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/src")

from utils.util import canonical_dns_name, short_hostname
from utils.parse_boolean import *
from utils.env import get_env_bool
from utils.log_impl import *

def canonical_name(ip_addr: str|list, omit_final_dot:bool = False) -> str:
    name = str(ip_addr)
    name_len = len(name)
    
    name_dot = name.rfind(".")
    if name_dot < (name_len - 1) and omit_final_dot == False:
        name += "."
    elif name.endswith(".") and omit_final_dot == True:  
        name = name.rstrip(".")
    return name

DEBUG_TRACE = os.environ.get("DEBUG_TRACE")
print("DEBUG_TRACE:", DEBUG_TRACE)

#from typing import Any

#def canonical_name(text_str: str, omit_final_dot:bool = False):
    #name = str(text_str)
    #name_len = len(name)

    #name_dot = name.rfind(".")
    #if name_dot < (name_len - 1) and omit_final_dot == False:
        #name += "."
    #elif name.endswith(".") and omit_final_dot == True:
      #name = name.rstrip(".")
    #return name

print("\n...unused (original) canonical DNS name tests...\n")

name_label = ""
res = canonical_name(name_label, False)
print("canonical_name; zero length w/o dot:", res)

name_label = ""
res = canonical_name(name_label, True)
print("canonical_name; zero length w/ dot:", res)

name_label = "home.arpa"
res = canonical_name(name_label, True)
print("non_canonical_name:", res)

name_label = "home.arpa"
res = canonical_name(name_label, False)
print("canonical_name:", res)

name_label = "home.arpa."
res = canonical_name(name_label, True)
# IMPORTANT(JEFF): This should never contain the last char, i.e.: `.`
print("non_canonical_name:", res)

name_label = "home.arpa."
res = canonical_name(name_label, False)
# IMPORTANT(JEFF): This should never contain the last char, i.e.: `.`
print("canonical_name:", res)

print("\n...newest canonical DNS name tests...\n")

name_label = "."
res = canonical_dns_name(name_label, False)
print("canonical_name; zero length w/ dot:", res)

name_label = "."
res = canonical_dns_name(name_label, True)
print("canonical_name; zero length w/o dot:", res)

name_label = "scorpio.home.arpa"
res = canonical_dns_name(name_label, True)
print("non_canonical_name:", res)

name_label = "scorpio.home.arpa"
res = canonical_dns_name(name_label, False)
print("canonical_name:", res)

name_label = "scorpio.home.arpa."
res = canonical_dns_name(name_label, True)
# IMPORTANT(JEFF): This should never contain the last char, i.e.: `.`
print("non_canonical_name:", res)

name_label = "scorpio.home.arpa."
res = canonical_dns_name(name_label, False)
# IMPORTANT(JEFF): This should never contain the last char, i.e.: `.`
print("canonical_name:", res)

print("\n...clean_hostname function unit tests...\n")

assert_res: str = ""
assert_answer = "scorpio"
assert_message = f'hostname must be {assert_answer}'

hostname = "scorpio.home.arpa"
assert_res = short_hostname(hostname)
assert assert_res == assert_answer, assert_message

hostname = "scorpio.home.arpa."
assert_res = short_hostname(hostname)
assert assert_res == assert_answer, assert_message

hostname = "scorpio.~"
assert_res = short_hostname(hostname)
assert assert_res == assert_answer, assert_message

hostname = "scorpio"
assert_res = short_hostname(hostname)
assert assert_res == assert_answer, assert_message

hostname = ""
assert_res = short_hostname(hostname)
assert assert_res == "", "hostname must remain zero-length"

