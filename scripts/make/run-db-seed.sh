#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-db-seed"

log_title "DATABASE SEED"

log_info "Creating superuser (if not exists)..."
python manage.py createsuperuser --noinput 2>/dev/null || log_warning "Superuser already exists"

log_info "Done"
