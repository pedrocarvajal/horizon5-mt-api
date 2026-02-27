#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
source "$(dirname "$0")/../helpers/docker.sh"
log_setup "run-db-seed-database"

log_title "DATABASE SEED"

log_info "Running seed_database command..."
docker_compose exec horizon-mt-api-web uv run python manage.py seed_database

log_info "Done"
