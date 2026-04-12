#!.venv/bin/python3

import os
import sys
import yaml # pyyaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/src")
FIXTURES_DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/test/fixtures"

#from utils.util import *

from enum import Enum
from utils.AppConfig import AppConfig

# version 1
APP_CONFIG = FIXTURES_DATA_DIR + '/app.yml'
app = AppConfig(APP_CONFIG)
assert app.path() == APP_CONFIG

app.set_path(APP_CONFIG)
assert app.path() == APP_CONFIG

config = app.dump()

assert config['version'] == 1
assert config['pdns_api_host'] == 'ns4.home'
assert config['pdns_api_port'] == 8081
assert config['pdns_api_proto'] == 'http'
assert config['pdns_api_certificate'] == 'None'

res = app.lookup_forward("ha.home.arpa")
# zone name, TSIG auth key, nameservers
ans = {
  'name': 'ha.home.arpa', 'key-name': 'sw2-axfr', 'dns-servers': [{'ip-address': '192.168.12.15', 'port': 5300}, {'ip-address': '192.168.12.16', 'port': 5300}]
}
assert res == ans
#print(res["dns-servers"][0])
#print(res["dns-servers"][1])

res = app.lookup_reverse("14.168.192.in-addr.arpa")
ans = {
  'name': '14.168.192.in-addr.arpa', 'key-name': 'sw2-axfr', 'dns-servers': [{'ip-address': '192.168.12.15', 'port': 5300}, {'ip-address': '192.168.12.16', 'port': 5300}]
}
assert res == ans
#print(res["dns-servers"][0])
#print(res["dns-servers"][1])

# version 2
APP_CONFIG = FIXTURES_DATA_DIR + '/app.v2.yml'
app = AppConfig(APP_CONFIG)
assert app.path() == APP_CONFIG

app.set_path(APP_CONFIG)
assert app.path() == APP_CONFIG

config = app.dump()

assert config['version'] == 2

res = app.lookup_forward("ha.home.arpa")
print(res)
ans = {
  'name': 'ha.home.arpa', 'key-name': 'pdns-api', 'protocol': 'http', 'certificate': 'None', 'dns-servers': [{'ip-address': '192.168.12.15', 'port': 5300}, {'ip-address': '192.168.12.16', 'port': 5300}]
}
assert res['name'] == 'ha.home.arpa'
assert res['dns-servers'][0]['port'] == 5300
assert res == ans

assert {'api_host': 'ns4'} == app.options()
assert app.api_host() == 'ns4'
# ?? version 2
#res = app.find_zone("ha.home.arpa")
#res = app.find_ptr_zone("14.168.192.in-addr.arpa")

