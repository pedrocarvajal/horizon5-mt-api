#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-linter-fixes"

log_title "LINTER FIXES"

log_info "Applying ruff formatting..."
uv run ruff format .

log_info "Running ruff auto-fix..."
uv run ruff check --fix .

log_info "Done"
