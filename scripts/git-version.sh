#!/bin/sh
#
#
# shellcheck shell=sh
#

ARGS="$1"

if [ -n "$ARGS" ]; then
  git rev-parse HEAD
else
  git rev-parse --short HEAD
fi

