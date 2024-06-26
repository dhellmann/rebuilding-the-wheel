#!/bin/bash
# -*- indent-tabs-mode: nil; tab-width: 2; sh-indentation: 2; -*-

# Tests full bootstrap and installation of a complex package, without
# worrying about isolating the tools from upstream sources or
# restricting network access during the build. This allows us to test
# the overall logic of the build tools separately from the isolated
# build pipelines.

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# shellcheck disable=SC1091
source "${SCRIPTDIR}/common.sh"

toplevel=${1:-langchain}

WORKDIR=$(pwd)/work-dir-${PYTHON_VERSION}
export WORKDIR
mkdir -p "$WORKDIR"

"${SCRIPTDIR}/../pipelines/bootstrap.sh" "${1:-langchain}"

find wheels-repo/simple/ -name '*.whl'

"${SCRIPTDIR}/../install-from-mirror.sh" "${toplevel}"
