#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-docker-down"

log_title "DOCKER COMPOSE DOWN"

log_info "Stopping and removing containers..."
docker compose down --remove-orphans

log_info "Done"
