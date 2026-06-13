---
created: 2026-02-12
authors: ["Jeffrey Carpenter <1329364+i8degrees@users.noreply.github.com"]
tags:
  - openwrt
  - ujail
  - dnsmasq
  - script
  - ddns
  - DNSMASQ_DOMAIN
---

# ddns_update

*WIP* ...

## usage

- `ddns_update --help`
- `ddns_update --version`

```shell
# append DDNS entry to zone
PDNS_API_KEY=xxx DNSMASQ_DOMAIN=test.arpa DNSMASQ_LOG_DHCP=1 \
    .venv/bin/ddns_update -lDEBUG \
ADD 02:xx:xx:AA 127.0.0.1 testme

# append DDNS entry to zone records in addition to reverse lookup zone
PDNS_API_KEY=xxx DNSUPDATE_ZONE_PTR=15.168.192.in-addr.arpa DNSMASQ_DOMAIN=test.arpa DNSMASQ_LOG_DHCP=1 \
    .venv/bin/ddns_update -lDEBUG \
ADD 02:xx:xx:AA 127.0.0.1 testme

# remove DDNS entry from zone
PDNS_API_KEY=xxx DNSMASQ_DOMAIN=test.arpa DNSMASQ_LOG_DHCP=1 \
    .venv/bin/ddns_update -lDEBUG \
DEL 02:xx:xx:AA 127.0.0.1 testme

# minimum necessary to invoke command
PDNS_API_KEY=xxx .venv/bin/ddns_update ADD 02:xx:xx:AA 127.0.0.1 testme
```

### development


```shell
python3 -m venv .venv
.venv/bin/python3 -m pip install build
.venv/bin/python3 -m build
pip install -r requirements.txt
pip install -e ddns_update[dev]
pip install -e .
# build dist packages and upload to host for dev deployment
scripts/build.sh
```

#### deployment
```shell
pipx install update_ddns_zone-1.1.0.tar.gz
# second phase of deployment; upload to host for bootstrap
scripts/deploy.sh
```

## Foot Notes

