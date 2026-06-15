#!/bin/sh
# shellcheck shell=sh
#
# TODO(JEFF): This script is a placeholder until I get around to replacing it.
#

#DEPLOY_PACKAGES=(
  #"config/app.yml"
  #"dist/update_ddns_zone-1.0.0.tar.gz"
#)

# package
#DEPLOY_PACKAGE_VERSION=1.1.0
DEPLOY_PACKAGE_VERSION="$(cat pyproject.toml | tomlq .project.version)"
# package filename
DEPLOY_PACKAGE_FILENAME=$1
if [ -z "$DEPLOY_PACKAGE_FILENAME" ]; then
  echo "CRIT: not a valid file path..."
  echo
  exit 1
fi

#DEPLOY_PACKAGE_FILENAME=update_ddns_zone-${DEPLOY_PACKAGE_VERSION}.tar.gz 
DEPLOY_PACKAGE_PATH="${DEPLOY_PACKAGE_FILENAME}" # local path

# deploy host
DEPLOY_USER=root # remote user
DEPLOY_HOST=sw2-gw.lan # remote host
SSH_HOST_STR="${DEPLOY_USER}@${DEPLOY_HOST}"
# TODO(JEFF): Prefer rsync?
DEPLOY_CMD=scp # local
DEPLOY_RUN_CMD=ssh # local
DEPLOY_PACKAGE_DEST="/tmp" # remote path

# 1a. Transfer dist package to deployment host
if ! $DEPLOY_CMD -O "${DEPLOY_PACKAGE_PATH}" ${SSH_HOST_STR}:${DEPLOY_PACKAGE_DEST}/.; then
  echo "CRIT: Failed to transfer ${DEPLOY_PACKAGE_PATH} at ${SSH_HOST_STR} - halting!"
  echo
  exit 1
fi

#DEPLOY_CONFIG="config/app.yml" # local path
#DEPLOY_CONFIG_DEST="/usr/local/etc/app.yml" # remote path
DEPLOY_CONFIG="config/app.json" # local path
DEPLOY_CONFIG_DEST="/usr/local/etc/app.json" # remote path

# 1b. Copy configuration file
# >> Do not fear if this fails -- we may have the file locked with chattr +i
# >> in order to prevent changes.
if ! $DEPLOY_CMD -O ${DEPLOY_CONFIG} ${SSH_HOST_STR}:${DEPLOY_CONFIG_DEST}; then
  echo "WARN: Failed to transfer ${DEPLOY_CONFIG} at ${SSH_HOST_STR} - continuing."
  echo
  #exit 2
fi

DEPLOY_PACKAGE_DEST=templates/openwrt/usr/lib/dnsmasq
DEPLOY_PACKAGE_FILENAME=dhcp-script.sh
# 1c. Copy template(s)
#if ! "${DEPLOY_RUN_CMD}" ${SSH_HOST_STR} "${DEPLOY_PACKAGE_DEST}/${DEPLOY_PACKAGE_FILENAME}"; then
  #echo "CRIT: Failed to transfer ${DEPLOY_PACKAGE_FILENAME} at ${SSH_HOST_STR} - halting!"
  #echo
  #exit 3
#fi


DEPLOY_PACKAGE_DEST=/tmp
# 2. Install package on host
if ! "${DEPLOY_RUN_CMD}" ${SSH_HOST_STR} pipx install --force "${DEPLOY_PACKAGE_DEST}/${DEPLOY_PACKAGE_FILENAME}"; then
  echo "CRIT: Failed to transfer ${DEPLOY_CONFIG} at ${SSH_HOST_STR} - halting!"
  echo
  exit 3
fi

# 3. Setup dist package
echo "ssh ${SSH_HOST_STR}" "service dnsmasq restart"

