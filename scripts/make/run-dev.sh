#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
source "$(dirname "$0")/../helpers/docker.sh"
log_setup "run-dev"

log_title "STARTING DEV ENVIRONMENT"

log_info "Starting database services..."
docker_compose up -d horizon-mt-api-postgres horizon-mt-api-mongodb

log_info "Waiting for databases to be healthy..."
docker_compose up horizon-mt-api-migrate

log_info "Running Django development server..."
uv run python manage.py runserver 0.0.0.0:8000
