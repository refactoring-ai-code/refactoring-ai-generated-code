#!/usr/bin/env sh
set -eu

ACTION="${1:-up}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
COMPOSE_FILE="$SCRIPT_DIR/compose.dev.yml"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker with the Compose plugin is required." >&2
  exit 1
fi

case "$ACTION" in
  up) docker compose -f "$COMPOSE_FILE" up --build --wait ;;
  down) docker compose -f "$COMPOSE_FILE" down ;;
  logs) docker compose -f "$COMPOSE_FILE" logs --follow ;;
  config) docker compose -f "$COMPOSE_FILE" config --quiet ;;
  *)
    echo "Usage: $0 [up|down|logs|config]" >&2
    exit 2
    ;;
esac
