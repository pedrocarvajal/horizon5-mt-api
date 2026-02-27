#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
source "$(dirname "$0")/../helpers/docker.sh"
log_setup "run-tests"

log_title "RUNNING TESTS"

log_info "Executing pytest..."
docker_compose exec horizon-mt-api-web uv run python -m pytest -v

log_info "Done"
