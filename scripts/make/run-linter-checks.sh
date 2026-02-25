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
ruff format --check "$TARGET"

log_info "Running ruff lint checks..."
ruff check "$TARGET"

log_info "Running pyright type checks..."
pyright

log_info "All checks passed"
