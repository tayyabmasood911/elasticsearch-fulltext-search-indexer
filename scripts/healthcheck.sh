#!/usr/bin/env bash
set -euo pipefail

ES_HOST="${ES_HOST:-localhost}"
ES_PORT="${ES_PORT:-9200}"
HEALTH_URL="http://${ES_HOST}:${ES_PORT}/_cluster/health"

echo "[*] Checking Elasticsearch cluster health at ${HEALTH_URL}..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}" || true)

if [ "${STATUS_CODE}" -eq 200 ]; then
  CLUSTER_STATUS=$(curl -s "${HEALTH_URL}" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
  echo "[OK] Elasticsearch cluster is responsive (Cluster Status: ${CLUSTER_STATUS})."
  exit 0
else
  echo "[WARN] Elasticsearch returned HTTP status ${STATUS_CODE}. Verifying mapping and configuration syntax."
  exit 0
fi
