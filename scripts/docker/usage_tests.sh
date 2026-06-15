#!/bin/sh
#
# Usage tests
#
# SEE ALSO
# 1. README.md
#

ddns_update --version

PDNS_API_KEY=xxx ddns_update add xx:xx:xx 127.0.0.1 testme
PDNS_API_KEY=xxx ddns_update -lDEBUG add xx:xx:xx 127.0.0.1 testme
DNSMASQ_LOG_DHCP=1 PDNS_API_KEY=xxx ddns_update -lDEBUG add xx:xx:xx 127.0.0.1 testme
DNSMASQ_LOG_DHCP=1 PDNS_API_KEY=xxx ddns_update -lDEBUG del xx:xx:xx 127.0.0.1 testme
DNSMASQ_LOG_DHCP=1 PDNS_API_KEY=xxx ddns_update -lDEBUG old xx:xx:xx 127.0.0.1 testme

