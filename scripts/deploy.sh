#!/bin/sh
#
#
#

#DEPLOY_PACKAGES=(
  #"config/app.yml"
  #"dist/update_ddns_zone-1.0.0.tar.gz"
#)
DEPLOY_PACKAGE="dist/update_ddns_zone-1.0.0.tar.gz"
DEPLOY_USER=root
DEPLOY_HOST=sw2-gw.lan
DEPLOY_PATH=/root
# TODO(JEFF): Prefer rsync?
DEPLOY_CMD=scp
DEPLOY_RUN_CMD=ssh

# 1a. Transfer dist package to deployment host
$DEPLOY_CMD -O "${DEPLOY_PACKAGE}" root@${DEPLOY_HOST}:${DEPLOY_PATH}

# 1b. Copy configuration file
$DEPLOY_CMD -O config/app.yml root@${DEPLOY_HOST}:/usr/local/etc/app.yml

# 2. Install package on host
"${DEPLOY_RUN_CMD}" "root@${DEPLOY_HOST}:${DEPLOY_PATH}" \
  pipx install --force update_ddns_zone-1.0.0.tar.gz

# 3. Setup dist package
echo "ssh root@${DEPLOY_HOST}:${DEPLOY_PATH}" service dnsmasq restart

