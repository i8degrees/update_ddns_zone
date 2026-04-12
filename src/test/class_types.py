#!.venv/bin/python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ "/src")

from utils.types import RRType, FQDN, IPHost, RR_A, RR_TXT, RR_PTR, RRset

ptr_req = RRset(RR_PTR(IPHost('192.168.12.150', FQDN('scorpio.home.arpa'))))
print(ptr_req.json())

record = RRset(RRType.A_RECORD)
record.name = "name_record"
record.content = "data"
assert record.type == RRType.A_RECORD
assert record.name == "name_record"
assert record.ttl == 60
assert record.content == "data"
#print(record.json())

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
