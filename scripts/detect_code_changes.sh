#!/usr/bin/env bash
set -euo pipefail

echo "Detecting code changes..."

EVENT="${GITHUB_EVENT_NAME:-}"
BASE_REF="${GITHUB_BASE_REF:-}"
RUN_TESTS=true

if [[ "$EVENT" == "pull_request" && -n "$BASE_REF" ]]; then
  git fetch origin "$BASE_REF":"refs/remotes/origin/$BASE_REF" --depth=1
  CHANGED_FILES=$(git diff --name-only "origin/$BASE_REF"...HEAD)

  echo "Changed files:"
  echo "$CHANGED_FILES"

  RUN_TESTS=false
  for f in $CHANGED_FILES; do
    case "$f" in
      *.md|docs/*|.github/workflows/*)
        ;;
      *)
        RUN_TESTS=true
        break
        ;;
    esac
  done
fi

echo "run_tests=$RUN_TESTS" >> "$GITHUB_OUTPUT"
