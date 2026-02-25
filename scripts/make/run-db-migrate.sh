#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-db-migrate"

log_title "DATABASE MIGRATIONS"

log_info "Running Django migrations..."
docker compose exec horizon-mt-api-web uv run python manage.py migrate

log_info "Done"
