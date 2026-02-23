# ?? FIXME errors from mypy

import errno
import json
import os
import sys
from dotenv import dotenv_values
from typing import Final # type: ignore

from utils import *
#from utils.util import * # util.py
#from utils.parse_boolean import * # parse_boolean.py
#from utils.env import * # env.py
#from utils.log_impl import *

config = {
    **os.environ,
    **dotenv_values(".env"),
    **dotenv_values(".env.dev"),
    **dotenv_values(".env.prod"),
}

assert config != None

PDNS_CHANGE_TYPE: Final[str] = "REPLACE"
PDNS_API_URL: Final[str] = config["PDNS_API_PROTO"] + "://" + config["PDNS_API_HOST"] \
    + ":" + str(config["PDNS_API_PORT"])

assert config["PDNS_API_VERSION"] != None, "PDNS_API_VERSION must be initialized"

log_debug("nsupdate-env", "Using v" + config["PDNS_API_VERSION"] + " PDNS Auth API")
print("DEBUG=" + config["DEBUG"])
print("VERBOSE=" + config["VERBOSE"])
print("SYSLOG=" + config["SYSLOG"])

def usage_info(name: str, exit_code: int):
  script_name = str(name)
  code = int(exit_code)
  
  print(script_name, "usage [AOD] [MAC_ADDRESS] [IP_ADDRESS] [HOSTNAME]")
  print()
  print(script_name, "...where [AOD] is one of (ADD|OLD|DEL)")
  print(script_name, "...where [MAC_ADDRESS] is a colon separated xx:xx:xx:xx:xx:xx")
  print(script_name, "...where [IP_ADDRESS] is a IPv4 address")
  print(script_name, "...where [HOSTNAME] is the non-fully-qualified hostname")
  print()
  print(f'{script_name} ADD c2:b9:8f:da:1b:29 192.168.12.150 testme')
  print(f'{script_name} OLD c2:b9:8f:da:1b:29 192.168.12.150 testme')
  print(f'{script_name} DEL c2:b9:8f:da:1b:29 192.168.12.150 testme')
  print(f'DNSMASQ_DOMAIN=ha.home.arpa {script_name} ADD c2:b9:8f:da:1b:29 192.168.12.150 testme')
  
  if code > 0:
    exit(code)

def main() -> None:
  args = sys.argv
  num_args = len(args)
  log_debug("nsupdate", "num_args:" + str(num_args))

  # !! IMPORTANT(JEFF): DNSMASQ_DOMAIN is a required environment variable of which is
  # only passed to this script when the end-user has dnsmasq configured with
  # an explicit domain. See the dnsmasq manual page regarding the `--domain`
  # parameter.
  DNSMASQ_DOMAIN = \
    canonical_dns_name(get_env("DNSMASQ_DOMAIN"))

  # >> NOTE(JEFF): This is for our convenience during development of this script.
  if not get_env("DNSMASQ_DOMAIN") and parse_boolean(config["DEBUG"]) == True:
    DNSMASQ_DOMAIN = canonical_dns_name("home.arpa")

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
    #DNSUPDATE_ZONE_PTR = canonical_dns_name("home.arpa.168.192.in-addr.arpa")
  elif DNSMASQ_DOMAIN == canonical_dns_name("ha.home.arpa"):
    # !! IMPORTANT(JEFF): This is required for the REST endpoint data input for PTR
    # !! zone updates
    DNSUPDATE_ZONE_PTR = "14.168.192.in-addr.arpa."
    #DNSUPDATE_ZONE_PTR = canonical_dns_name("ha.home.arpa.168.192.in-addr.arpa")

  print("DNSMASQ_DOMAIN:", DNSMASQ_DOMAIN)
  print("DNSUPDATE_ZONE_PTR:", DNSUPDATE_ZONE_PTR)

  # !! Required argument
  try:
    # ?? TODO(JEFF): Rename AOD to DNSMASQ_CMD
    AOD = args[1].lower() # (ADD|OLD|DEL)
  except IndexError:
    crit("nsupdate", "Missing script argument AOD")
    usage_info("nsupdate.py", EXIT_PARAMS)
  
  # !! Required argument
  # >> DNSMASQ may pass DUID made of the link layer *...* instead of
  # >> See man 8 dnsmasq
  # >> RFC XXX
  try:
    # ?? TODO(JEFF): Rename MAC to MAC_ADDRESS
    MAC = str(args[2])
  except IndexError:
    crit("nsupdate", "Missing script argument MAC")
    usage_info("nsupdate.py", EXIT_PARAMS)
  
  # !! Required argument
  try:
    IP_ADDR = str(args[3])
    PTR = reverse_ip(IP_ADDR)
    RIP = f'{PTR}.in-addr.arpa.'
    #RIP = f'{PTR}.{DNSUPDATE_ZONE_PTR}'
  except IndexError:
    crit("nsupdate", "Missing script argument IP_ADDR")
    usage_info("nsupdate.py", EXIT_PARAMS)
  
  # !! Required argument
  try:
    L_HOSTNAME = short_hostname(str(args[4]))
    FQDN = canonical_dns_name(L_HOSTNAME) + canonical_dns_name(str(DNSMASQ_DOMAIN))
    log_debug("nsupdate", "FQDN:" + FQDN)
  except IndexError:
    crit("nsupdate", "Missing script argument HOSTNAME")
    usage_info("nsupdate.py", EXIT_PARAMS)

  assert MAC != "", "MAC must be a given argument to script"
  assert IP_ADDR != "", "IP_ADDR must be a given argument to script"
  assert L_HOSTNAME != "", "L_HOSTNAME must be a given argument to script"
  assert FQDN != "", "FQDN must be a given argument to script"

  # ?? TODO(JEFF): Use the enhanced EXTEND API when PDNS Auth server is newer 
  # ?? than 4.8.4; I am limited to v4.8.4 API until I upgrade the auth server on my end.
  # >> SEE ALSO
  # >> 1. https://doc.powerdns.com/authoritative/http-api/zone.html#adding-a-single-record-to-a-rrset
  if config["PDNS_API_VERSION"] >= "4.9.12":
    PDNS_CHANGE_TYPE = "EXTEND"

  PDNS_API_URL_SUFFIX = \
      "/api/v1/servers/localhost/zones"

  RR_TYPE_A_REQUEST = {
    "rrsets": [{
      "name": f'{FQDN}',
      "type": "A",
      "ttl": f'{config["PDNS_TTL"]}',
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
      "ttl": f'{config["PDNS_TTL"]}',
      # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
      "changetype": "REPLACE", # DELETE
      "records": [{
        # ?? TODO(JEFF): Lookup function for escaping this input; the REST endpoint
        # ?? requires this particular RR type to always have quotes surrounding it.
        "content": f'"{MAC}"',
        "disabled": False
      }]
    }]
  }

  RR_TYPE_PTR_REQUEST = {
    "rrsets": [{
      #"name": f'{RIP}.in-addr.arpa.',
      "name": f'{RIP}',
      "type": "PTR",
      "ttl": f'{config["PDNS_TTL"]}',
      # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
      "changetype": "REPLACE", # DELETE
      "records": [{
        "content": f'{FQDN}',
        "disabled": False
      }]
    }]
  }

  #verbose_debug("nsupdate", "wtf")

  #print("RR_TYPE_PTR_REQUEST_DEL:", json.dumps(RR_TYPE_PTR_REQUEST_DEL))

  FULL_REQUEST_URL = PDNS_API_URL + PDNS_API_URL_SUFFIX

  try:
    if AOD != "add" and AOD != "old" and AOD != "del":
      raise ValueError
  except ValueError:
    crit("nsupdate", "AOD must be one of: (ADD|OLD|DEL).")
    exit(EXIT_PARAMS)
  
  # !! Lease registration or renewal
  if AOD == "add" or AOD == "old":
    # >> NOTE(JEFF): The LOG_STR is purely for visual aid in log output
    LOG_STR = AOD
    if LOG_STR == "old":
      LOG_STR = "RENEW"
    elif LOG_STR == "add":
      LOG_STR = "NEW"
      
    verbose_debug(f'nsupdate-{LOG_STR}', "RR_TYPE_A_REQUEST: " + json.dumps(RR_TYPE_A_REQUEST))  
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = config["PDNS_API_KEY"], json_data = RR_TYPE_A_REQUEST)
    print(res.status_message)
    if res.status_code != 204:
      exit(res.status_code)
    
    verbose_debug(f'nsupdate-{LOG_STR}', "RR_TYPE_TXT_REQUEST: " + json.dumps(RR_TYPE_TXT_REQUEST))
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = config["PDNS_API_KEY"], json_data = RR_TYPE_TXT_REQUEST)
    print(res.status_message)
    if res.status_code != 204:
      exit(res.status_code)
    
    verbose_debug(f'nsupdate-{LOG_STR}', "RR_TYPE_PTR_REQUEST: " + json.dumps(RR_TYPE_PTR_REQUEST))
    res = update_record(url = FULL_REQUEST_URL, zone = DNSUPDATE_ZONE_PTR, api_key = config["PDNS_API_KEY"], json_data = RR_TYPE_PTR_REQUEST)
    print(res.status_message)
    if res.status_code != 204:
      exit(res.status_code)
  
  # !! Lease release
  elif AOD == "del":
    # >> NOTE(JEFF): The LOG_STR is purely for visual aid in log output
    LOG_STR="RELEASE"
    
    RR_TYPE_A_REQUEST_DEL = RR_TYPE_A_REQUEST
    RR_TYPE_A_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_A_REQUEST_DEL["rrsets"][0]["ttl"] = None
    verbose_debug(f'nsupdate-{LOG_STR}', "RR_TYPE_A_REQUEST_DEL: " + json.dumps(RR_TYPE_A_REQUEST_DEL))
    
    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = config["PDNS_API_KEY"], json_data = RR_TYPE_A_REQUEST_DEL)
    print(res.status_message)
    if res.status_code != 204:
      exit(res.status_code)

    RR_TYPE_TXT_REQUEST_DEL = RR_TYPE_TXT_REQUEST
    RR_TYPE_TXT_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_TXT_REQUEST_DEL["rrsets"][0]["ttl"] = None
    verbose_debug(f'nsupdate-{LOG_STR}', "RR_TYPE_TXT_REQUEST_DEL: " + json.dumps(RR_TYPE_TXT_REQUEST_DEL))

    res = update_record(url = FULL_REQUEST_URL, zone = DNSMASQ_DOMAIN, api_key = config["PDNS_API_KEY"], json_data = RR_TYPE_TXT_REQUEST_DEL)
    print(res.status_message)
    if res.status_code != 204:
      exit(res.status_code)
      
    RR_TYPE_PTR_REQUEST_DEL = RR_TYPE_PTR_REQUEST
    RR_TYPE_PTR_REQUEST_DEL["rrsets"][0]["changetype"] = "DELETE"
    RR_TYPE_PTR_REQUEST_DEL["rrsets"][0]["ttl"] = None
    verbose_debug(f'nsupdate-{LOG_STR}', "RR_TYPE_PTR_REQUEST_DEL: " + json.dumps(RR_TYPE_PTR_REQUEST_DEL))     
    res = update_record(url = FULL_REQUEST_URL, zone = DNSUPDATE_ZONE_PTR, api_key = config["PDNS_API_KEY"], json_data = RR_TYPE_PTR_REQUEST_DEL)
    print(res.status_message)
    if res.status_code != 204:
      exit(res.status_code)

if __name__ == "__main__":
  main(num_args, args)
