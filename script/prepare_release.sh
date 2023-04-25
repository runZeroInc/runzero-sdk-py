#!/usr/bin/env bash

LC_ALL=C

set -euo pipefail

function _err() {
  >&2 echo "Error: $*, exiting"
  exit 1
}

function _usage() {
  local _name="${0##*/}"
  >&2 echo "Prepares this project for release by bumping the project version and creating a signed, annotated git tag"
  >&2 echo "Usage: $_name [-h] {-b BUMP_RULE | -v VERSION}"
  >&2 echo "   -b, --bump,              A type of release to create using one of the following bump rule names:"
  >&2 echo "                                patch minor major"
  >&2 echo "                            Automatically updates the version number according to semver principles"
  >&2 echo "                            May not also specify --direct-version"
  >&2 echo ""
  >&2 echo "   -v, --direct-version,    The direct version string."
  >&2 echo "                            Must be semver-compliant and in form e.g. 1.2.3"
  >&2 echo "                            May not also specify --bump"
  >&2 echo ""
  >&2 echo "Examples using bump rules (preferred):"
  >&2 echo "   > $_name -b patch  # prepare PATCH release with fixes only, no new features, no breaking change"
  >&2 echo "   > $_name -b minor  # prepare MINOR release with new features, no breaking change"
  >&2 echo "   > $_name -b major  # prepare MAJOR release breaking change"
  >&2 echo ""
  >&2 echo "Example using direct version specification (discouraged):"
  >&2 echo "   > $_name -v 0.10.1  # PATCH"
  >&2 echo "   > $_name -v 0.11.0  # MINOR"
  >&2 echo "   > $_name -v 1.11.0  # MAJOR"
  >&2 echo ""
  >&2 exit 1
}

VERSION_CMD_TARGET=""

function _valid_version() {
  [[ -n "$1" ]] || _err "must provide version string to direct version flag"
  [[ "$1" =~ ^([0-9]+\.){2}[0-9]$ ]]
}

function _set_direct_version() {
  if [[ -n "$VERSION_CMD_TARGET" ]]; then
    _err "cannot set bump rule and direct version simultaneously"
  fi
  if ! _valid_version "$1"; then
    _err "'$1' is not a valid version, e.g. 0.2.0"
  fi
  VERSION_CMD_TARGET="$1"
}

function _set_bump_rule() {
  if [[ -n "$VERSION_CMD_TARGET" ]]; then
    _err "cannot set bump rule and direct version number simultaneously"
  fi
  [[ -n "$1" ]] || _err "must provide bump rule name to bump flag"
  if ! [[ "$1" =~ ^major|minor|patch$ ]]; then
    >&2 echo "Error: '$1' is not a valid bump rule name"
    _usage
  fi

  VERSION_CMD_TARGET="$1"
}

function _check_poetry() {
  local _poetry
  _poetry="$(command -v poetry)"
  if [ -z "$_poetry" ]; then
    _err "cannot find poetry"
    exit 1
  fi
  >&2 printf "Using %s at %s\n" "$(poetry --version)" "$_poetry"
}

function _bump_project() {
  local _version_string_or_bump_rule="$1"
  poetry version --no-interaction "$_version_string_or_bump_rule"
}

function _current_project_version() {
  poetry version -s
}

function _tag_name() {
  _version="$1"
  echo "v${_version}"
}

function _apply_signed_release_tag() {
  local _tag_name="$1"
  git tag --annotate --sign "${_tag_name}" --message ":release: $_tag_name"
}

function _check_built_with_version() {
  local _check_ver="$1"
  local _build_out
  _build_out="$(poetry build --no-interaction)"
  local _verline
  _verline="$(echo "$_build_out" | head -n 1)"
  local _expected="Building runzero-sdk ($_check_ver)"
  [[ "$_verline" == "$_expected" ]] || _err "build output line '$_verline' did not match '$_expected'"
}

function _repo_is_clean() {
  [[ -z "$(git status -s)" ]]
}

function _commit_release() {
  local _ver_msg="$1"
  local _git_root
  _git_root="$(git rev-parse --show-toplevel)" || _err "cannot find root of git repository"
  git add "$_git_root/pyproject.toml" && \
  git commit -m "Release version $_ver_msg"
}

# ---- main ----

if [ $# -eq 0  ]; then
  _usage
fi

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -h|--help) _usage; shift ;;
        -b|--bump) _set_bump_rule "$2"; shift ;;
        -v|--direct-version) _set_direct_version "$2"; shift ;;
        *) >&2 echo "Unknown parameter passed: $1"; _usage ;;
    esac
    shift
done


_check_poetry
_repo_is_clean || _err "will not prepare release with untracked, modified, or staged files in repo"

_bump_project "$VERSION_CMD_TARGET" || _err "failed to apply new version to project"
NEW_VER="$(_current_project_version)"
_check_built_with_version "$NEW_VER"

_commit_release "$NEW_VER" || _err "could not commit pyproject.toml"

RELEASE_TAG="$(_tag_name "$NEW_VER")"
{ _apply_signed_release_tag "$RELEASE_TAG" && git push origin "${RELEASE_TAG}"; } || {
   git reset --hard "HEAD^"
   git tag -d "${RELEASE_TAG}" 2>/dev/null
  _err "failed to apply signed git release tag and push, reverted"
}

echo "Successfully prepared the project for release"
ORIGIN_URL="$(git config --get remote.origin.url)"
if ! [[ "$ORIGIN_URL" =~ ^https://$ ]]; then
  ORIGIN_URL="$(echo "$ORIGIN_URL"  | sed -e 's/:/\//g' \
                                  | sed -e 's/ssh\/\/\///g' \
                                  | sed -e 's/git@/https:\/\//g' \
                                  | sed -e 's/\.git$//g' )"
fi

if [[ "$ORIGIN_URL" =~ ^https://$ ]]; then
  echo "You may create a release for $RELEASE_TAG at:"
  echo "$ORIGIN_URL/tags"
fi
