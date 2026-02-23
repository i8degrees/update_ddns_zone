#!.venv/bin/python3

import os
import sys
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/src")
FIXTURES_DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/test/fixtures"

from utils.util import *

from enum import Enum
from utils.parse_boolean import *
#from parse_boolean import parse_boolean
from utils.env import *
from logging import *
from utils.util import *

print(FIXTURES_DATA_DIR)
APP_CONFIG = FIXTURES_DATA_DIR + '/app.yml'
print(APP_CONFIG)
app: str = ""
with open(APP_CONFIG, 'r') as file:
    app = yaml.safe_load(file)
print(f'version: {app['version']}')
print(f'proto: {app['pdns_api_proto']}')
print(f'cert: {app['pdns_api_certificate']}')
print(f'api_key: {app['pdns_api_key']}')
print(f'ns: {app['forward-ddns']}')
