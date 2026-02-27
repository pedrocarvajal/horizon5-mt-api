#!/bin/bash

resolve_compose_file() {
  local env="${APP_ENV:-local}"

  case "$env" in
  production)
    echo "docker-compose.prod.yml"
    ;;
  *)
    echo "docker-compose.yml"
    ;;
  esac
}

docker_compose() {
  local compose_file
  compose_file=$(resolve_compose_file)
  docker compose -f "$compose_file" "$@"
}
