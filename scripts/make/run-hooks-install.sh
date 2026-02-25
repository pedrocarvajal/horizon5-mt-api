#!/bin/bash
set -e

source "$(dirname "$0")/../helpers/logger.sh"
log_setup "run-hooks-install"

log_title "GIT HOOKS INSTALL"

log_info "Setting git hooks path to .githooks/..."
git config core.hooksPath .githooks

log_info "Making hooks executable..."
chmod +x .githooks/*

log_info "Done"
