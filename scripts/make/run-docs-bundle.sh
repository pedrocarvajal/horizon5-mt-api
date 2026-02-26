#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-docs-bundle"

log_title "API DOCS BUNDLE"

log_info "Bundling OpenAPI spec..."
npx @redocly/cli bundle docs/api/openapi.yaml -o docs/api/openapi-dist.yaml

log_info "Bundle created at docs/api/openapi-dist.yaml"
