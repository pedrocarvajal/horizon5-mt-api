#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-tests"

log_title "RUNNING TESTS"

log_info "Executing pytest..."
python -m pytest -v

log_info "Done"
