#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
source "$(dirname "$0")/../helpers/docker.sh"
log_setup "run-docker-build"

log_title "DOCKER COMPOSE BUILD"

log_info "Building images..."
docker_compose build

log_info "Done"
