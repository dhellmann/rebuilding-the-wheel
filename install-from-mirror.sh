#!/bin/bash

set -xe

PYTHON=${PYTHON:-python3.9}

# Redirect stdout/stderr to logfile
logfile="install-mirror-${PYTHON}.log"
exec > >(tee "$logfile") 2>&1

VENV=$(basename $(mktemp --dry-run --directory --tmpdir=. venvXXXX))
HTTP_SERVER_PID=

on_exit() {
  [ "$HTTP_SERVER_PID" ] && kill $HTTP_SERVER_PID
  rm -rf $VENV/
}
trap on_exit EXIT SIGINT SIGTERM

setup() {
  $PYTHON -m venv $VENV
  . ./$VENV/bin/activate
  pip install -U pip
}

setup

toplevel=${1:-langchain}

$PYTHON -m http.server --directory wheels-repo/ 9090 &
HTTP_SERVER_PID=$!

pip -vvv install \
    --disable-pip-version-check \
    --no-cache-dir \
    --index-url http://localhost:9090/simple \
    --upgrade \
    "${toplevel}"
pip freeze

# --dry-run --ignore-installed --report report.json
