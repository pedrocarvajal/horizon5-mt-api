#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
source "$(dirname "$0")/../helpers/docker.sh"
log_setup "run-dev-tailscale"

log_title "STARTING DEV ENVIRONMENT (TAILSCALE)"

log_info "Starting database services..."
docker_compose up -d horizon-mt-api-postgres horizon-mt-api-mongodb

log_info "Running database migrations..."
docker_compose run --rm horizon-mt-api-web uv run python manage.py migrate

log_info "Starting application services..."
docker_compose up -d horizon-mt-api-web horizon-mt-api-scheduler

TAILSCALE_BIN=$(which tailscale 2>/dev/null || echo "/Applications/Tailscale.app/Contents/MacOS/Tailscale")
TAILSCALE_IP=$("$TAILSCALE_BIN" ip -4 2>/dev/null || echo "")

if [ -z "$TAILSCALE_IP" ]; then
  log_warning "Tailscale not running or not connected — skipping port forward"
else
  log_info "Starting Tailscale port forward: $TAILSCALE_IP:8000 -> 127.0.0.1:8000"
  python3 "$(dirname "$0")/../tailscale_forward.py" "$TAILSCALE_IP" 8000 &
  FORWARD_PID=$!
  trap "kill $FORWARD_PID 2>/dev/null; exit" INT TERM EXIT
  log_info "Port forward running (PID $FORWARD_PID)"
  log_info "Tailscale access: http://$TAILSCALE_IP:8000"
fi

log_info "Development server running on http://localhost:8000"
docker_compose logs -f horizon-mt-api-web
