#!/usr/bin/env bash
set -euo pipefail

echo "Checking for docs-only changes..."

EVENT="${GITHUB_EVENT_NAME:-}"
BASE_REF="${GITHUB_BASE_REF:-}"
RUN_TESTS=1

if [[ "$EVENT" == "pull_request" && -n "$BASE_REF" ]]; then
  # PR merge refs are commonly checked out with depth=1. Fetch enough base
  # history to establish a merge-base; if that still fails, fail safe by
  # running tests rather than incorrectly classifying the change as docs-only.
  git fetch --no-tags origin "$BASE_REF":"refs/remotes/origin/$BASE_REF" --depth=128

  if MERGE_BASE=$(git merge-base "origin/$BASE_REF" HEAD 2>/dev/null); then
    CHANGED_FILES=$(git diff --name-only "$MERGE_BASE" HEAD)

    echo "Changed files:"
    echo "$CHANGED_FILES"

    RUN_TESTS=0
    for f in $CHANGED_FILES; do
      case "$f" in
        *.md|docs/*)
          ;;
        .github/workflows/*)
          ;;
        *)
          RUN_TESTS=1
          break
          ;;
      esac
    done
  else
    echo "No merge-base available; fail-safe: run tests."
    RUN_TESTS=1
  fi
fi

if [[ "$RUN_TESTS" -eq 0 ]]; then
  echo "Docs/workflows-only change detected. Skipping tests."
  exit 0
fi

echo "Code changes detected. Proceeding with tests."
