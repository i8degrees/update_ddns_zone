#!/bin/sh
#
#
#

# 1. Build distribution package
VENV_PREFIX="$1"
if [ -z "$VENV_PREFIX" ]; then
  VENV_PREFIX=".venv/bin"
fi

$VENV_PREFIX/python3 -m pip install build
$VENV_PREFIX/python3 -m build

