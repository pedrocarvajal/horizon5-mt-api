#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
source "$(dirname "$0")/../helpers/docker.sh"
log_setup "run-dev"

log_title "STARTING DEV ENVIRONMENT"

log_info "Starting database services..."
docker_compose up -d horizon-mt-api-postgres horizon-mt-api-mongodb

log_info "Running database migrations..."
docker_compose run --rm horizon-mt-api-web uv run python manage.py migrate

log_info "Starting application services..."
docker_compose up -d horizon-mt-api-web horizon-mt-api-scheduler

log_info "Development server running on http://localhost:8000"
docker_compose logs -f horizon-mt-api-web
