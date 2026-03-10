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

APP_CONFIG = FIXTURES_DATA_DIR + '/app.yml'
app: str = ""
with open(APP_CONFIG, 'r') as file:
    app = yaml.safe_load(file)

assert app['version'] == 1
assert app['pdns_api_host'] == 'ns4.home'
assert app['pdns_api_proto'] == 'http'
assert app['pdns_api_certificate'] == 'None'
assert app['pdns_api_key'] == 'dnsFuckboobsYeah'
#print(f'ns: {app['forward-ddns']}')

class AppConfig:
    app = {}
    def __init__(self, path: str = ''):
        self.path = path
        self.load_yaml(self.path)
        
    def load_yaml(self, path: str = ''):
        with open(self.path, 'r') as file:
            app = yaml.safe_load(file)
            
    def path(self):
        return self.path
    
    def set_path(self, path_str: str = ''):
        self.path = path_str
    
    def dump(self) -> dict:
        # return app['version']
        return app

app_config = AppConfig(APP_CONFIG)
assert app_config.path == APP_CONFIG
app_config.set_path(APP_CONFIG)
assert app_config.path == APP_CONFIG

app = app_config.dump()
assert app['version'] == 1
assert app['pdns_api_host'] == 'ns4.home'
assert app['pdns_api_port'] == 8081


