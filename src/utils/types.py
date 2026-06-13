
from enum import Enum
from utils.parse_boolean import parse_boolean
from logging import *
from utils.util import *

class RRType(Enum):
  A_RECORD = "A"
  AAAA_RECORD = "AAAA"
  CNAME_RECORD = "CNAME"
  DHCID_RECORD = "DHCID"
  PTR_RECORD = "PTR"
  TXT_RECORD = "TXT"

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
    def hash(self) -> str:
        return ""

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
        
#class RR_PTR(RRset):
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

""" Super type class for RR_A, RR_TXT & friends
RRset(RR_PTR)
"""
class RRset:
    def __init__(self, any) -> None:
        self.type = any
        self.name = any.name or None
        self.ttl = int(60)
        # FIXME
        #self.content = any.data or None
        self.content = None
        self.disabled = False
        self.comments = str("")

    # Render JSON representable object of class
    def json(self) -> dict:
        result: dict = {
            "rrsets": [{
              "name": f'{self.name}',
              "type": self.type,
              "ttl": self.ttl,
              # ?? TODO(JEFF): Use EXTEND API when PDNS_API_VERSION >= 4.9.12
              "changetype": "REPLACE", # DELETE
              "records": [{
                "content": f'{self.content}',
                "disabled": self.disabled,
              }]
            }]
        }
        return result
