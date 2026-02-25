#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-docker-up"

log_title "DOCKER COMPOSE UP"

log_info "Starting all services..."
docker compose up -d

log_info "Done"
