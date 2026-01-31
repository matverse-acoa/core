#!/usr/bin/env bash
set -euo pipefail

echo "Checking for docs-only changes..."

EVENT="${GITHUB_EVENT_NAME:-}"
BASE_REF="${GITHUB_BASE_REF:-}"
RUN_TESTS=1

if [[ "$EVENT" == "pull_request" && -n "$BASE_REF" ]]; then
  echo "PR detected. Base ref: $BASE_REF"
  git fetch origin "$BASE_REF" --depth=1

  CHANGED_FILES=$(git diff --name-only FETCH_HEAD...HEAD)

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
fi

if [[ "$RUN_TESTS" -eq 0 ]]; then
  echo "Docs/workflows-only change detected. Skipping tests."
  exit 0
fi

echo "Code changes detected. Proceeding with tests."
