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
    **os.environ,
}

log = logging.getLogger('ddns_psupdate')

app = None

PROG_NAME = 'ddns_psupdate'
PROG_VERSION = '%(prog)s 1.0.0'
# ?? import utils for __version__ def
PROG_VERSION = '%(prog)s ' + __version__
DESCRIPTION = 'Update DNS upon DHCP lease'
DEFAULT_LOG_LEVELS = ["DEBUG", "NOTICE", "INFO", "WARNING", "CRITICAL", "ERROR"]
DEFAULT_CONFIG_FILE_PATH = "config/app.yml"
DEFAULT_LOG_LEVEL = 'INFO'
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
                    help="Enable debugging code")
parser.add_argument("-l", "--log", default=DEFAULT_LOG_LEVEL,
    help=f'Set the log level to one of {DEFAULT_LOG_LEVELS}')
parser.add_argument("-v", "--version", action="version", version=PROG_VERSION)

args = parser.parse_args()
DEBUG = bool(args.debug)
LOG_LEVEL = DEFAULT_LOG_LEVEL
if args.log.upper() in DEFAULT_LOG_LEVELS:
    LOG_LEVEL = args.log.upper()
CMD = args.CMD.lower()
MAC_ADDR = args.MAC_ADDR
IP_ADDR = args.IP_ADDR
HOSTNAME = args.HOSTNAME
APP_CONFIG = args.config

if APP_CONFIG:
    if not (os.path.isfile(APP_CONFIG) and os.access(APP_CONFIG, os.R_OK)):
      print(f"ERROR: The given file path at {args.config} does not exist.")
      exit(1)
    else:
       print(f"Found configuration file at {APP_CONFIG}")
       app = AppConfig(APP_CONFIG)

if LOG_LEVEL == "DEBUG":
  log.setLevel(logging.DEBUG)
elif LOG_LEVEL == "NOTICE":
  log.setLevel(logging.NOTICE)
elif LOG_LEVEL == "INFO":
  log.setLevel(logging.INFO)
elif LOG_LEVEL == "WARNING":
  log.setLevel(logging.WARNING)
elif LOG_LEVEL == "CRITICAL":
  log.setLevel(logging.CRITICAL)
elif LOG_LEVEL == "ERROR":
  log.setLevel(logging.ERROR)

print(LOG_LEVEL)
if DEBUG == True:
  print("DEBUGGING is on")
  
config = app.dump()

# !! This is ultimately left up to the end-user to decide of which they wish
# to do; this must be set in either case.
PDNS_API_KEY: str = ""
if config.get("PDNS_API_KEY") != None:
    PDNS_API_KEY = config["PDNS_API_KEY"]
else:
    PDNS_API_KEY = get_env("PDNS_API_KEY", "")
assert PDNS_API_KEY != "", "The PDNS_API_KEY (X-API-Key) must be initialized."

PDNS_API_VERSION: str = ""
if config.get("PDNS_API_VERSION") != None:
    PDNS_API_VERSION = config["PDNS_API_VERSION"]
else:
    PDNS_API_VERSION = get_env("PDNS_API_VERSION", "4.8.4")
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

def main() -> None:
  args = sys.argv

  # !! IMPORTANT(JEFF): DNSMASQ_DOMAIN is a required environment variable of which is
  # only passed to this script when the end-user has dnsmasq configured with
  # an explicit domain. See the dnsmasq manual page regarding the `--domain`
  # parameter.
  DNSMASQ_DOMAIN = \
    canonical_dns_name(get_env("DNSMASQ_DOMAIN", ""))

  DNSUPDATE_ZONE_PTR = \
    canonical_dns_name(get_env("DNSUPDATE_ZONE_PTR", ""))

  # >> NOTE(JEFF): This is for our convenience during development of this script.
  #if not get_env("DNSMASQ_DOMAIN", "") and DEBUG == True:
    #DNSMASQ_DOMAIN = canonical_dns_name("test.home.arpa")

  DNSUPDATE_ZONE_PTR: Final[str|None] = None

  # >> HACK(JEFF): This is a monkey patch for until we figure out a proper 
  # >> configuration format for this script that matches the domain with the
  # >> reverse zone in which updates should be applied to. If the configuration
  # >> file is missing, we simply do not touch the reverse zone mappings 
  # >> whatsoever.
  if DNSMASQ_DOMAIN == canonical_dns_name("home.arpa"):
    # !! IMPORTANT(JEFF): This is required for the REST endpoint data input for PTR
    # !! zone updates
    DNSUPDATE_ZONE_PTR = "12.168.192.in-addr.arpa."
    #DNSUPDATE_ZONE_PTR = canonical_dns_name("12.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("ha.home.arpa"):
    # !! IMPORTANT(JEFF): This is required for the REST endpoint data input for PTR
    # !! zone updates
    DNSUPDATE_ZONE_PTR = "11.168.192.in-addr.arpa."
    #DNSUPDATE_ZONE_PTR = canonical_dns_name("11.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("iot.ha.home.arpa"):
    # !! IMPORTANT(JEFF): This is required for the REST endpoint data input for PTR
    # !! zone updates
    DNSUPDATE_ZONE_PTR = "14.168.192.in-addr.arpa."
    #DNSUPDATE_ZONE_PTR = canonical_dns_name("14.168.192.in-addr.arpa")
  
  log.debug(f'DNSMASQ_DOMAIN: {DNSMASQ_DOMAIN}')
  log.debug(f'DNSUPDATE_ZONE_PTR: {DNSUPDATE_ZONE_PTR}')
  
  # !! Required argument
  # >> DNSMASQ may pass DUID made of the link layer *...* instead of
  # >> See man 8 dnsmasq
  # >> RFC XXX
    
  PTR = reverse_ip(IP_ADDR)
  RIP = f'{PTR}.in-addr.arpa.'
  #RIP = f'{PTR}.{DNSUPDATE_ZONE_PTR}'
  #L_HOSTNAME = short_hostname(str(args[4]))
  L_HOSTNAME = short_hostname(HOSTNAME)
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
      "changetype": "REPLACE", # DELETE
      "records": [{
        "content": IP_ADDR,
        "disabled": False
      }]
    }]
  }

  RR_TYPE_TXT_REQUEST = {
    "rrsets": [{
      "name": f'{FQDN}',
      "type": "TXT",
      "ttl": f'{config["PDNS_API_TTL"]}',
      # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
      "changetype": "REPLACE", # DELETE
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
      "changetype": "REPLACE", # DELETE
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
  
  # !! Lease registration or renewal
  if CMD == "add" or CMD == "old":
    # >> NOTE(JEFF): The LOG_STR is purely for visual aid in log output
    LOG_STR = CMD
    if LOG_STR == "old":
      LOG_STR = "RENEW"
    elif LOG_STR == "add":
      LOG_STR = "NEW"
      
    log.debug(f'{LOG_STR}-RR_TYPE_A_REQUEST:{json.dumps(RR_TYPE_A_REQUEST)}')
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_A_REQUEST)
    print(res.message())
    if res.status_code() != 204:
      exit(res.status_code())
    
    log.debug(f'{LOG_STR}-RR_TYPE_TXT_REQUEST:{json.dumps(RR_TYPE_TXT_REQUEST)}')
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_TXT_REQUEST)
    print(res.message())
    if res.status_code() != 204:
      exit(res.status_code())
    
    if DNSUPDATE_ZONE_PTR != None:
      log.debug(f'{LOG_STR}-RR_TYPE_PTR_REQUEST:{json.dumps(RR_TYPE_PTR_REQUEST)}')
      res = update_record(url = FULL_REQUEST_URL, zone = DNSUPDATE_ZONE_PTR, api_key = PDNS_API_KEY, json_data = RR_TYPE_PTR_REQUEST)
      print(res.message())
      if res.status_code() != 204:
        exit(res.status_code())

  # !! Lease release
  elif CMD == "del":
    # >> NOTE(JEFF): The LOG_STR is purely for visual aid in log output
    LOG_STR="RELEASE"
    
    RR_TYPE_A_REQUEST_DEL = RR_TYPE_A_REQUEST
    RR_TYPE_A_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_A_REQUEST_DEL["rrsets"][0]["ttl"] = None
    log.debug(f'{LOG_STR}-RR_TYPE_A_REQUEST_DEL:{json.dumps(RR_TYPE_A_REQUEST_DEL)}')
    
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_A_REQUEST_DEL)
    print(res.status_message())
    if res.status_code() != 204:
      exit(res.status_code())

    RR_TYPE_TXT_REQUEST_DEL = RR_TYPE_TXT_REQUEST
    RR_TYPE_TXT_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_TXT_REQUEST_DEL["rrsets"][0]["ttl"] = None
    log.debug(f'{LOG_STR}-RR_TYPE_TXT_REQUEST_DEL:{json.dumps(RR_TYPE_TXT_REQUEST_DEL)}')

    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = PDNS_API_KEY, json_data = RR_TYPE_TXT_REQUEST_DEL)
    print(res.status_message())
    if res.status_code() != 204:
      exit(res.status_code())
    
    if DNSUPDATE_ZONE_PTR != None:
      RR_TYPE_PTR_REQUEST_DEL = RR_TYPE_PTR_REQUEST
      RR_TYPE_PTR_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
      RR_TYPE_PTR_REQUEST_DEL["rrsets"][0]["ttl"] = None
      log.debug(f'{LOG_STR}-RR_TYPE_PTR_REQUEST_DEL:{json.dumps(RR_TYPE_PTR_REQUEST_DEL)}')
    
      res = update_record(url = FULL_REQUEST_URL, zone = DNSUPDATE_ZONE_PTR, api_key = PDNS_API_KEY, json_data = RR_TYPE_PTR_REQUEST_DEL)
      print(res.status_message())
      if res.status_code() != 204:
        exit(res.status_code())
