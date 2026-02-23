#!.venv/bin/python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/src")

from utils.util import *

from enum import Enum
from utils.parse_boolean import *
#from parse_boolean import parse_boolean
from utils.env import *
from logging import *
from utils.util import *

class RRType(Enum):
  A_RECORD = "A"
  PTR_RECORD = "PTR"
  TXT_RECORD = "TXT"
  DHCID_RECORD = "DHCID"

class FQDN:

    def __init__(self, hostname) -> None:
        self.host = canonical_dns_name(hostname)

    def hostname(self) -> list|None:
        host = self.host.split(".")
        return host[0]

    def fqdn(self) -> str:
        return self.host

    def set(self, hostname) -> None:
        self.host = hostname
        
    def origin(self) -> str:
        zone = self.host.split(".")
        result = zone[1] + "." + zone[2]

class IPHost:
    def __init__(self, ipaddr, FQDN) -> None:
        self.ip_addr = ipaddr # 4 octets (array)
        self.host = FQDN
    
    def ip_address(self):
        return self.ip_addr
    
    def hostname(self):
        return self.host.hostname()
    
    def fqdn(self):
        return self.host.fqdn()

    def origin(self):
        return self.host.origin()

class RR_A:
    def __init__(self, IPHost) -> None:
        self.type = RRType.A_RECORD        
        self.name = IPHost
        self.data = self.name.ip_address()
        self.ttl = int(0)
        self.disabled = False
        self.comments = str("")

    def record(self) -> IPHost:
        return { 
            self.name.fqdn(), 
            self.name.ip_address() 
        }

    def set_ttl(self, ttl: int) -> None:
        self.ttl = int(ttl) # seconds

    def set_disabled(self, val: bool) -> None:
        self.disabled = parse_boolean(val)
    def set_comments(self, val: list) -> None:
        self.comments = val

class RR_TXT:
    # content can be any
    def __init__(self, FQDN, content: str = "") -> None:
        self.type = RRType.TXT_RECORD
        self.name = FQDN
        self.data = f'{content}' # proper sanitization is critical
        self.ttl = int(0)
        self.disabled = False
        self.comments = str("")

    def record(self) -> FQDN:
        return { 
            self.name.hostname(), 
            self.name.fqdn(), 
            #self.name.origin() 
        }
    
    def set_ttl(self, ttl: int) -> None:
        self.ttl = int(ttl) # seconds
        
    def set_data(self, content: str) -> None:
        self.data = f'{content}'
        
    def set_disabled(self, val: bool) -> None:
        self.disabled = parse_boolean(val)
    def set_comments(self, val: list) -> None:
        self.comments = val
        
class RR_PTR:
    
    def __init__(self, IPHost) -> None:
        self.type = RRType.PTR_RECORD
        self.name = IPHost
        self.data = self.name.fqdn()
        self.ttl = int(0)
        self.disabled = False
        self.comments = str("")
    
    def record(self) -> IPHost:
        ip_addr = self.name.ip_address()
        ptr = reverse_ip(ip_addr)
        rip_str = f'{ptr}.in-addr.arpa.' # make canonical 
        return { 
            self.name.fqdn(),
            rip_str,
        }

    def set_ttl(self, ttl: int) -> None:
        self.ttl = int(ttl) # seconds
        
    #def set_data(self, content: str) -> None:
        #self.data = f'{content}'
        
    def set_disabled(self, val: bool) -> None:
        self.disabled = parse_boolean(val)
    def set_comments(self, val: list) -> None:
        self.comments = val
    
scorpio = FQDN('scorpio.home.arpa')

assert scorpio.hostname() == "scorpio"
assert scorpio.fqdn() == "scorpio.home.arpa."
scorpio.set('virgo.home.arpa')
assert scorpio.hostname() == "virgo"

host = IPHost("192.168.12.150", FQDN("scorpio.home.arpa"))
assert host.ip_address() == "192.168.12.150"
assert host.hostname() == "scorpio"
assert host.fqdn() == "scorpio.home.arpa."

a_req = RR_A(host)
print(a_req.record())
assert a_req.record() == { '192.168.12.150', 'scorpio.home.arpa.' }
assert a_req.ttl == 0
a_req.set_ttl(60)
assert a_req.ttl == 60
assert a_req.type == RRType.A_RECORD
assert a_req.disabled == False
a_req.set_disabled(True)
assert a_req.disabled == True
assert a_req.data == '192.168.12.150'

txt_req = RR_TXT(FQDN('virgo.home.arpa'), '02:xx:ff:bb:ce')
print(txt_req.record())
assert txt_req.record() == { 'virgo', 'virgo.home.arpa.' }
assert txt_req.data == '02:xx:ff:bb:ce'
assert txt_req.ttl == 0
txt_req.set_ttl(60)
assert txt_req.ttl == 60
assert txt_req.type == RRType.TXT_RECORD
assert txt_req.disabled == False
txt_req.set_disabled(True)
assert txt_req.disabled == True

txt_req = RR_TXT(FQDN('virgo.home.arpa'))
assert txt_req.record() == { 'virgo', 'virgo.home.arpa.' }
assert txt_req.data == ''
assert txt_req.ttl == 0
txt_req.set_ttl(60)
assert txt_req.ttl == 60
assert txt_req.type == RRType.TXT_RECORD
assert txt_req.disabled == False
txt_req.set_disabled(True)
assert txt_req.disabled == True

ptr_req = RR_PTR(IPHost('192.168.12.150', FQDN('scorpio.home.arpa')))
print(ptr_req.record())
assert ptr_req.record() == { '150.12.168.192.in-addr.arpa.', 'scorpio.home.arpa.' }
assert ptr_req.ttl == 0
ptr_req.set_ttl(60)
assert ptr_req.ttl == 60
assert ptr_req.type == RRType.PTR_RECORD
assert ptr_req.disabled == False
ptr_req.set_disabled(True)
assert ptr_req.disabled == True
