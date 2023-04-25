#!/usr/bin/env bash

# Performs basic install check in a clean environment, and that the version string matches

set -e

PROJ_ROOT="$(git rev-parse --show-toplevel)"

(
pushd "$PROJ_ROOT" || { >&2 echo "cannot enter project root" && exit 1; }
[ -d ./dist ] && rm -rf ./dist 2>&1
mkdir dist && poetry build
PROJ_VER="$(poetry version -s)"
PY="$(which python)"
>&2 echo "creating virtualenv"
# shellcheck disable=SC1091
"$PY" -m venv .testinst && . .testinst/bin/activate
pip install dist/runzero_sdk-*.tar.gz
# get out of project root to ensure we're importing from installed copy
[ -d "$PROJ_ROOT/build" ] || mkdir "$PROJ_ROOT/build" 2>&1
pushd "$PROJ_ROOT/build" || { >&2 echo "cannot enter build dir" && exit 1; }
INST_VER=$( python -c 'import runzero as runzero; c=runzero.Client(); print(runzero.__version__)' )
popd
[ -z "$INST_VER" ] && { >&2 echo "Could not execute installed package and get version" && exit 1; }
if [ "$INST_VER" != "$PROJ_VER" ]; then
  >&2 echo "FAILED clean install version check"
  >&2 echo "Installed version $INST_VER does not match pyproject.toml version $PROJ_VER"
  exit 1
fi

echo "$INST_VER" OK
deactivate && rm -rf .testinst 2>&1
)
