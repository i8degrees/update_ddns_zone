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

### development


```shell
python3 -m build
python3 -m venv .venv
pip install -r requirements.txt
pip install -e .
# build dist packages and upload to host for dev deployment
scripts/build.sh
```

#### deployment
```shell
pipx install update_ddns_zone-1.0.0.tar.gz
# second phase of deployment; upload to host for bootstrap
scripts/deploy.sh
```

## Foot Notes

