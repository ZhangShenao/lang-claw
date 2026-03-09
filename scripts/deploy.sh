#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"

if [[ ! -f ".env" ]]; then
  echo ".env not found. Create it from .env.example before deployment."
  exit 1
fi

set -a
source .env
set +a

RUNNING_CONTAINERS="$(docker ps -q)"
if [[ -n "${RUNNING_CONTAINERS}" ]]; then
  echo "Stopping running Docker containers..."
  docker stop ${RUNNING_CONTAINERS}
fi

docker compose down
docker compose build --no-cache
docker compose up -d --force-recreate

echo "Waiting for backend health endpoint..."
for _ in {1..30}; do
  if curl -fsS "http://localhost:${BACKEND_PORT:-8000}/api/health" >/dev/null 2>&1; then
    echo "Deployment succeeded."
    echo "Frontend: http://localhost:${FRONTEND_PORT:-3000}"
    echo "Backend:  http://localhost:${BACKEND_PORT:-8000}"
    exit 0
  fi
  sleep 2
done

echo "Deployment started, but backend healthcheck did not become ready in time."
exit 1
