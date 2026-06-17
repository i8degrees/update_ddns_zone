# ?? FIXME errors from mypy

import errno
import json
import os
import sys

import argparse
from typing import Final # type: ignore
from utils import *

import logging

env = {
    **os.environ
}

# shell env applicable to this service app
env.setdefault("PDNS_API_KEY", "")
env.setdefault("PDNS_API_VERSION", "4.8.4")
env.setdefault("DNSMASQ_DOMAIN", canonical_dns_name("localhost.test"))
env.setdefault("DNSUPDATE_ZONE_PTR", None)
env.setdefault("DNSMASQ_LOG_DHCP", False)
env.setdefault("DNSMASQ_TAGS", "")
env.setdefault("DNSMASQ_INTERFACE", "")
env.setdefault("DNSMASQ_DATA_MISSING", False)

log = logging.getLogger('ddns_psupdate')

app = None

PROG_NAME = 'ddns_psupdate'
PROG_VERSION = '%(prog)s ' + 'v' + __version__ + ' at git SHA ' + __gitversion__
DESCRIPTION = 'Update DNS upon DHCP lease'
#DEFAULT_CONFIG_FILE_PATH = "config/app.yml"
DEFAULT_CONFIG_FILE_PATH = "config/app.json"
DEFAULT_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "WARNING" # 30
DEBUG = False
DEFAULT_CMD_OPTS = ["ADD", "OLD", "DEL"]

parser = \
  argparse.ArgumentParser(prog=PROG_NAME, description=DESCRIPTION)
parser.add_argument("CMD", help=f'Command is one of {DEFAULT_CMD_OPTS}')
parser.add_argument("MAC_ADDR",
                    help="The 48-bit link-layer address")
parser.add_argument("IP_ADDR", type=str,
                    help="Client IPv4 address")
parser.add_argument("HOSTNAME", type=str,
                    help="Client's (short) hostname")
parser.add_argument("-c", "--config", default=DEFAULT_CONFIG_FILE_PATH,
                    help=f"The file path to the configuration file")
parser.add_argument("-d", "--debug", action="store_true",
                    help="Enable extra debug code")
parser.add_argument("-l", "--log", default=DEFAULT_LOG_LEVEL,
                    help=f'Set the log level to one of {DEFAULT_LOG_LEVELS}')
parser.add_argument("-v", "--version", action="version", version=PROG_VERSION)

args = parser.parse_args()
DEBUG = bool(args.debug)

log_level = DEFAULT_LOG_LEVEL
if args.log.upper() in DEFAULT_LOG_LEVELS:
  log_level = args.log.upper()

numeric_log_level = getattr(logging, log_level.upper(), None)

if not isinstance(numeric_log_level, int):
  raise ValueError('Invalid log level: %s' % log_level)
log.setLevel(numeric_log_level)

APP_CONFIG = args.config

if APP_CONFIG:
  if not (os.path.isfile(APP_CONFIG) and os.access(APP_CONFIG, os.R_OK)):
    print(f"ERROR: The given file path at {APP_CONFIG} does not exist.")
    exit(1)
  else: 
    if log_level == "DEBUG":
        print(f"Found configuration file at {APP_CONFIG}")
    app = AppConfig(APP_CONFIG)

log.debug(f'LOG_LEVEL={log_level}')

config = app.dump()

# !! This is ultimately left up to the end-user to decide of which they wish
# to do; this must be set in either case.
PDNS_API_KEY = env["PDNS_API_KEY"]
if config.get("PDNS_API_KEY") != None:
  PDNS_API_KEY = config["PDNS_API_KEY"]
else:
  PDNS_API_KEY = env["PDNS_API_KEY"]
assert PDNS_API_KEY != "", "The PDNS_API_KEY (X-API-Key) must be initialized."

PDNS_API_VERSION: str = ""
if config.get("PDNS_API_VERSION") != None:
  PDNS_API_VERSION = config["PDNS_API_VERSION"]
else:
  PDNS_API_VERSION = env["PDNS_API_VERSION"]
assert PDNS_API_VERSION != "", "PDNS_API_VERSION must be initialized"

# !! Initial default
PDNS_CHANGE_TYPE: Final[str] = "REPLACE"

# ?? TODO(JEFF): Use the enhanced EXTEND API when PDNS Auth server is newer
# ?? than 4.8.4; I am limited to v4.8.4 API until I upgrade the auth server
# on my end.
# >> SEE ALSO
# >> 1. https://doc.powerdns.com/authoritative/http-api/zone.html#adding-a-single-record-to-a-rrset
if PDNS_API_VERSION >= "4.9.12":
  PDNS_CHANGE_TYPE = "EXTEND"

# FIXME(JEFF): This should be handled in update_record or so in utils/util.py
PDNS_API_URL: Final[str] = config["PDNS_API_PROTO"] + "://" + \
    config["PDNS_API_HOST"] \
+ ":" + str(config["PDNS_API_PORT"])

DNSMASQ_LOG_DHCP = \
    env["DNSMASQ_LOG_DHCP"]
if DNSMASQ_LOG_DHCP and bool(DNSMASQ_LOG_DHCP) == True:
    print("Verbose DHCP logging is enabled.")
    log.setLevel(9);

DNSMASQ_TAGS = \
    env["DNSMASQ_TAGS"]
if DNSMASQ_TAGS and len(DNSMASQ_TAGS) > 0:
    print(f'DNSMASQ_TAGS={DNSMASQ_TAGS}')

DNSMASQ_INTERFACE = \
    env["DNSMASQ_INTERFACE"]
if DNSMASQ_INTERFACE and len(DNSMASQ_INTERFACE) > 0:
    print(f'DNSMASQ_INTERFACE={DNSMASQ_INTERFACE}')

# >> This env is set to "1" (True) during "old" events and signifies to
# >> us -- at the very minimum -- that we do not need to iterate through
# >> the main loop as there is nothing to be done.
DNSMASQ_DATA_MISSING = \
    env["DNSMASQ_DATA_MISSING"]
if DNSMASQ_DATA_MISSING and bool(DNSMASQ_DATA_MISSING) == True:
    print("DNSMASQ_DATA_MISSING=1\nExiting...\n")
    sys.exit(0);

# !! IMPORTANT(JEFF): DNSMASQ_DOMAIN is a required environment variable of which is
# only passed to this script when the end-user has dnsmasq configured with
# an explicit domain. See the dnsmasq manual page regarding the `--domain`
# parameter.
DNSMASQ_DOMAIN = \
  canonical_dns_name(env["DNSMASQ_DOMAIN"])

# ?? Rename to DNSMASQ_DOMAIN_PTR
# !! IMPORTANT(JEFF): This is required for the REST endpoint data input for PTR
# !! zone updates

def main() -> None:
  #args = sys.argv

  # >> HACK(JEFF): This is a monkey patch for until we figure out a proper 
  # >> configuration format for this script that matches the domain with the
  # >> reverse zone in which updates should be applied to. If the configuration
  # >> file is missing, we simply do not touch the reverse zone mappings 
  # >> whatsoever.
  if DNSMASQ_DOMAIN == canonical_dns_name("home.arpa"):
    DNSUPDATE_ZONE_PTR = canonical_dns_name("12.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("ha.home.arpa"):
    DNSUPDATE_ZONE_PTR = canonical_dns_name("11.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("iot.ha.home.arpa"):
    DNSUPDATE_ZONE_PTR = canonical_dns_name("14.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("iot.home.arpa"):
    DNSUPDATE_ZONE_PTR = canonical_dns_name("14.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("mgmt.home.arpa"):
     DNSUPDATE_ZONE_PTR = canonical_dns_name("13.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("wifi.home.arpa"):
     DNSUPDATE_ZONE_PTR = canonical_dns_name("16.168.192.in-addr.arpa")

  log.debug(f'DNSMASQ_DOMAIN={env["DNSMASQ_DOMAIN"]}')
  log.debug(f'DNSUPDATE_ZONE_PTR={env["DNSUPDATE_ZONE_PTR"]}')

  # !! FIXME
  assert DNSMASQ_DOMAIN != "None." and DNSMASQ_DOMAIN != "", "DNSMASQ_DOMAIN must be set"
  DNSUPDATE_ZONE_PTR = None
  if env["DNSUPDATE_ZONE_PTR"] and len(env["DNSUPDATE_ZONE_PTR"]) > 0:
    DNSUPDATE_ZONE_PTR = \
      canonical_dns_name(env["DNSUPDATE_ZONE_PTR"])
  else:
    DNSUPDATE_ZONE_PTR = None

  # !! Required argument
  # >> DNSMASQ may pass DUID made of the link layer *...* instead of
  # >> See man 8 dnsmasq
  # >> RFC XXX
  
  CMD = args.CMD.lower()
  MAC_ADDR = args.MAC_ADDR
  IP_ADDR = args.IP_ADDR
  L_HOSTNAME = short_hostname(args.HOSTNAME)
  
  PTR = reverse_ip(IP_ADDR)
  RIP = f'{PTR}.in-addr.arpa.'
  
  FQDN = canonical_dns_name(L_HOSTNAME) + canonical_dns_name(str(DNSMASQ_DOMAIN))
  log.debug(f'FQDN:{FQDN}')
  
  assert MAC_ADDR != "", "MAC must be a given argument to script"
  assert IP_ADDR != "", "IP_ADDR must be a given argument to script"
  assert L_HOSTNAME != "", "L_HOSTNAME must be a given argument to script"
  assert FQDN != "", "FQDN must be a given argument to script"

  PDNS_API_URL_SUFFIX = \
      "/api/v1/servers/localhost/zones"

  RR_TYPE_A_REQUEST = {
    "rrsets": [{
      "name": f'{FQDN}',
      "type": "A",
      "ttl": f'{config["PDNS_API_TTL"]}',
      # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
      "changetype": PDNS_CHANGE_TYPE,
      "records": [{
        "content": IP_ADDR,
        "disabled": False
      }]
    }]
  }
  #RRset request(RRType.DHCID_RECORD, name=FQDN, content=HASH)

  RR_TYPE_TXT_REQUEST = {
    "rrsets": [{
      "name": f'{FQDN}',
      "type": "TXT",
      "ttl": f'{config["PDNS_API_TTL"]}',
      # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
      "changetype": PDNS_CHANGE_TYPE,
      "records": [{
        # ?? TODO(JEFF): Lookup function for escaping this input; the REST endpoint
        # ?? requires this particular RR type to always have quotes surrounding it.
        "content": f'"{MAC_ADDR}"',
        "disabled": False
      }]
    }]
  }

  RR_TYPE_PTR_REQUEST = {
    "rrsets": [{
      #"name": f'{RIP}.in-addr.arpa.',
      "name": f'{RIP}',
      "type": "PTR",
      "ttl": f'{config["PDNS_API_TTL"]}',
      # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
      "changetype": PDNS_CHANGE_TYPE,
      "records": [{
        "content": f'{FQDN}',
        "disabled": False
      }]
    }]
  }

  FULL_REQUEST_URL = PDNS_API_URL + PDNS_API_URL_SUFFIX

  try:
    if CMD != "add" and CMD != "old" and CMD != "del":
      raise ValueError
  except ValueError:
    log.critical("CMD must be one of: (ADD|OLD|DEL).")
    exit(EXIT_PARAMS)

  ttl = config["PDNS_API_TTL"]
  # !! Lease registration or renewal
  if CMD == "add" or CMD == "old":
    # >> NOTE(JEFF): The LOG_STR is purely for visual aid in log output
    LOG_STR = CMD
    if LOG_STR == "old":
      LOG_STR = "RENEW"
    elif LOG_STR == "add":
      LOG_STR = "NEW"

    #RRset request(RRType.A_RECORD, name=FQDN, content=IP_ADDR)
    #request.json()
    if bool(DNSMASQ_LOG_DHCP) == True:
        print(f'{LOG_STR} RR_TYPE_A_REQUEST:{json.dumps(RR_TYPE_A_REQUEST).encode("utf-8")}')
    else:
        print(f'[{LOG_STR}] {FQDN} {ttl} IN A {IP_ADDR} at {PDNS_API_URL}')
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_A_REQUEST)
    if res.status_code() != 204:
        err = FetchError(res.status_code(), res.message(), {})
        print(f'    {err.message()} with status code {err.status_code()}')
    else:
        print(f'{res.status_message()}')

    #RRset request(RRType.TXT_RECORD, name=FQDN, content=MAC_ADDR)
    #request.json()
    if bool(DNSMASQ_LOG_DHCP) == True:
        print(f'{LOG_STR} RR_TYPE_TXT_REQUEST:{json.dumps(RR_TYPE_TXT_REQUEST).encode("utf-8")}')
    else:
        print(f'[{LOG_STR}] {FQDN} {ttl} IN TXT {IP_ADDR} at {PDNS_API_URL}')

    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_TXT_REQUEST)
    if res.status_code() != 204:
        err = FetchError(res.status_code(), res.message(), {})
        print(f'    {err.message()} with status code {err.status_code()}')
    else:
        print(f'{res.status_code()}')
    if DNSUPDATE_ZONE_PTR != None:
        #RRset request(RRType.PTR_RECORD, name=RIP, content=FQDN)
        #request.json()
        if bool(DNSMASQ_LOG_DHCP) == True:
            print(f'{LOG_STR} RR_TYPE_PTR_REQUEST:{json.dumps(RR_TYPE_PTR_REQUEST).encode("utf-8")}')
        else:
            print(f'[{LOG_STR}] {RIP} {ttl} IN PTR {FQDN} at {PDNS_API_URL}')
        res = update_record(url = FULL_REQUEST_URL, zone = DNSUPDATE_ZONE_PTR, api_key = PDNS_API_KEY, json_data = RR_TYPE_PTR_REQUEST)
        if res.status_code() != 204:
            err = FetchError(res.status_code(), res.message())
            print(f'    {err.message()} with status code {err.status_code()}')
        else:
            print(f'{res.status_code()}')
    else:
        print(f'Not updating PTR record because no reverse zone has been specified.')

  # !! Lease release
  elif CMD == "del":
    # >> NOTE(JEFF): The LOG_STR is purely for visual aid in log output
    LOG_STR="RELEASE"
    
    RR_TYPE_A_REQUEST_DEL = RR_TYPE_A_REQUEST
    RR_TYPE_A_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_A_REQUEST_DEL["rrsets"][0]["ttl"] = None
    if bool(DNSMASQ_LOG_DHCP) == True:
        print(f'{LOG_STR} RR_TYPE_A_REQUEST_DEL:{json.dumps(RR_TYPE_A_REQUEST_DEL).encode("utf-8")}')
    else:
        print(f'[{LOG_STR}] {FQDN} {ttl} IN A {IP_ADDR} at {PDNS_API_URL}')

    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_A_REQUEST_DEL)
    if res.status_code() != 204:
        err = FetchError(res.status_code(), res.message(), {})
        print(f'    {err.message()} with status code {err.status_code()}')
    else:
        print(f'{res.status_message()}')

    RR_TYPE_TXT_REQUEST_DEL = RR_TYPE_TXT_REQUEST
    RR_TYPE_TXT_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_TXT_REQUEST_DEL["rrsets"][0]["ttl"] = None
    if bool(DNSMASQ_LOG_DHCP) == True:
        print(f'{LOG_STR} RR_TYPE_TXT_REQUEST_DEL:{json.dumps(RR_TYPE_TXT_REQUEST_DEL).encode("utf-8")}')
    else:
        print(f'[{LOG_STR}] {FQDN} {ttl} IN TXT {IP_ADDR} at {PDNS_API_URL}')

    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_TXT_REQUEST_DEL)
    if res.status_code() != 204:
        err = FetchError(res.status_code(), res.message(), {})
        print(f'    {err.message()} with status code {err.status_code()}')
    else:
        print(f'{res.status_message()}')

    if DNSUPDATE_ZONE_PTR != None:
      RR_TYPE_PTR_REQUEST_DEL = RR_TYPE_PTR_REQUEST
      RR_TYPE_PTR_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
      RR_TYPE_PTR_REQUEST_DEL["rrsets"][0]["ttl"] = None
      if bool(DNSMASQ_LOG_DHCP) == True:
        print(f'{LOG_STR} RR_TYPE_PTR_REQUEST_DEL:{json.dumps(RR_TYPE_PTR_REQUEST_DEL).encode("utf-8")}')
      else:
        print(f'[{LOG_STR}] {RIP} {ttl} IN PTR {FQDN} at {PDNS_API_URL}')

      res = update_record(url = FULL_REQUEST_URL, zone = DNSUPDATE_ZONE_PTR, api_key = PDNS_API_KEY, json_data = RR_TYPE_PTR_REQUEST_DEL)
      if res.status_code() != 204:
        err = FetchError(res.status_code(), res.message(), {})
        print(f'    {err.message()} with status code {err.status_code()}')
      else:
        print(f'{res.status_message()}')
    else:
        print(f'Not removing PTR record because no reverse zone has been specified.')

