#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-linter-checks"

log_title "LINTER CHECKS"

TARGET="."
while [[ $# -gt 0 ]]; do
  case $1 in
  --file)
    TARGET="$2"
    shift 2
    ;;
  --folder)
    TARGET="$2"
    shift 2
    ;;
  *)
    shift
    ;;
  esac
done

log_info "Checking formatting with ruff format..."
uv run ruff format --check "$TARGET"

log_info "Running ruff lint checks..."
uv run ruff check "$TARGET"

log_info "Running pyright type checks..."
uv run pyright

log_info "All checks passed"
