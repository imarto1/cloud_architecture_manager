#!/usr/bin/env bash
set -euo pipefail

# Deploy all isolated LocalStack clouds and their named volumes.
SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="${LOCALSTACK_PROJECT_NAME:-cloud-architecture-mocks}"

docker compose \
  --parallel 10 \
  -f "${SCRIPT_DIRECTORY}/docker-compose.yml" \
  -p "${PROJECT_NAME}" \
  up --detach --wait
