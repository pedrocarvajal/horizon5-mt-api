#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-dev"

log_title "STARTING DEV ENVIRONMENT"

log_info "Building Docker images..."
docker compose build

log_info "Starting services..."
docker compose up -d horizon-mt-api-postgres horizon-mt-api-mongodb

log_info "Waiting for databases to be healthy..."
docker compose up horizon-mt-api-migrate

log_info "Running Django development server..."
python manage.py runserver 0.0.0.0:8000
