#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-get-producer-credentials"

log_title "GET PRODUCER CREDENTIALS"

log_info "Starting credentials wizard..."
docker compose exec horizon-mt-api-web uv run python manage.py get_producer_credentials

log_info "Done"
