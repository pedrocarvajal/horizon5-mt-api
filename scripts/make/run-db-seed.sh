#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-db-seed"

log_title "DATABASE SEED"

log_info "Running seed command..."
docker compose exec horizon-mt-api-web uv run python manage.py seed

log_info "Done"
