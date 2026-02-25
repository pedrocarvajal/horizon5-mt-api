#!/bin/bash

COLOR_RESET="\033[0m"
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_CYAN="\033[0;36m"
COLOR_BOLD="\033[1m"

LOG_FILE=""

log_setup() {
  local script_name="$1"
  mkdir -p "$(dirname "$0")/../../logs"
  LOG_FILE="$(dirname "$0")/../../logs/${script_name}.log"
}

_log_write() {
  local message="$1"
  local timestamp
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  if [ -n "$LOG_FILE" ]; then
    echo "[$timestamp] $message" >>"$LOG_FILE"
  fi
}

log_title() {
  local title="$1"
  echo ""
  echo -e "${COLOR_BOLD}========================================${COLOR_RESET}"
  echo -e "${COLOR_BOLD}  $title${COLOR_RESET}"
  echo -e "${COLOR_BOLD}========================================${COLOR_RESET}"
  echo ""
  _log_write "[TITLE] $title"
}

log_info() {
  local message="$1"
  echo -e "${COLOR_GREEN}[INFO]${COLOR_RESET} $message"
  _log_write "[INFO] $message"
}

log_warning() {
  local message="$1"
  echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} $message"
  _log_write "[WARN] $message"
}

log_error() {
  local message="$1"
  echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $message"
  _log_write "[ERROR] $message"
}

log_debug() {
  local message="$1"
  echo -e "${COLOR_CYAN}[DEBUG]${COLOR_RESET} $message"
  _log_write "[DEBUG] $message"
}
