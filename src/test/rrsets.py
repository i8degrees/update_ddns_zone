#!.venv/bin/python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/src")

from utils.util import *
from utils.parse_boolean import parse_boolean
from utils.env import *
from utils.log_impl import *

#RRType.A_RECORD
#RRType.TXT_RECORD
#RRType.PTR_RECORD
class RRType:
  A_RECORD = "A"
  PTR_RECORD = "PTR"
  TXT_RECORD = "TXT"
  DHCID_RECORD = "DHCID"

# scorpio.home.arpa.
# <hostname>.<origin>
# short_hostname
# canonical_hostname
class FQDN:
  host: str # hostname
  #origin : str # zone
  # getter
  def short_hostname() -> str:
    return short_hostname(host)
  
  def __init__(self, hostname: str) -> None:
    self.host = canonical_dns_name(hostname)
  
class IPHost:
  #host: str # FQDN class type
  #ip_addr: list # 4 octets
  
  def __init__(self, hostname: str, ipaddr: str) -> None:
    self.host = short_hostname(hostname)
    if type(ipaddr) == list:
        self.ip_addr = ipaddr.split()
    else:
        self.ip_addr = ipaddr

class RRset_A:
  IPHost(hostname="scorpio", ipaddr="192.168.12.150")
  #IPHost(ipaddr="192.168.12.150")
  FQDN("scorpio.home.arpa")
  
class RRset_PTR:
  FQDN
  IPHost
  
class RRset_MAC:
  FQDN
  IPHost

RRset = {
  "name": canonical_dns_name("."),
  "ip_addr": [],
  "ttl": 0
}

class RRset:
  fqdn = "" # FQDN
  type = "A" # RRType.A_RECORD
  ttl = 60 # 
  record = "" # ipHost
  extra_data = ""
  
  def init(fqdn, rr_type, ttl, content):
    type = rr_type.upper() in ["A", "TXT", "PTR"]
    ttl = int(ttl)
    if type == "A":
       fqdn = canonical_dns_name(fqdn)
       record = content
    elif type == "TXT":
      fqdn = canonical_dns_name(fqdn)
      record = str(type) # MAC
    elif type == "PTR":
      fqdn = reverse_ip(content)
      record = record
    
RRset.name = canonical_dns_name("testme.home.arpa")
RRset.type = "A"
RRset.ttl = 60
RRset.ip_addr = ["127.0.0.1"]
print(RRset)

RRset.setdefault("name", "")
RRset.setdefault("type", "A")
RRset.setdefault("ttl", 60)
RRset.setdefault("ip_addr", "")

print(RRset.ttl)
