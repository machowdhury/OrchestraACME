#!/usr/bin/env bash
# =============================================================================
# OrchestraACME — One-time local Splunk bootstrap (Docker Pattern A)
# Creates index + HEC token to match .env, fixes shared telemetry volume perms.
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Load .env if present
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

SPLUNK_PASSWORD="${SPLUNK_PASSWORD:-ACMEPassword2026!}"
SPLUNK_CONTAINER="${SPLUNK_CONTAINER:-acme_splunk}"
HEC_TOKEN="${SPLUNK_HEC_TOKEN:-acme-hec-token-0000-1111-2222-3333}"
HEC_INDEX="${SPLUNK_HEC_INDEX:-acme_agentic_telemetry}"
HEC_SOURCETYPE="${SPLUNK_HEC_SOURCETYPE:-otel:agentic:json}"
AUTH="admin:${SPLUNK_PASSWORD}"
SPLUNK_BIN="/opt/splunk/bin/splunk"

echo "[bootstrap] Waiting for Splunk container (${SPLUNK_CONTAINER})..."
for i in $(seq 1 60); do
  if docker exec "$SPLUNK_CONTAINER" curl -sf -k "https://localhost:8089/services/server/info" \
      -u "$AUTH" >/dev/null 2>&1; then
    echo "[bootstrap] Splunk management API is up."
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "[bootstrap] ERROR: Splunk not ready after 5 minutes. Check: docker compose logs splunk"
    exit 1
  fi
  sleep 5
done

echo "[bootstrap] Ensuring shared telemetry volume is writable..."
docker exec -u root "$SPLUNK_CONTAINER" sh -c \
  'mkdir -p /var/log/defenseclaw && chmod 1777 /var/log/defenseclaw' || true

echo "[bootstrap] Enabling HTTP Event Collector (global)..."
docker exec "$SPLUNK_CONTAINER" "$SPLUNK_BIN" http-event-collector enable -auth "$AUTH" || true

echo "[bootstrap] Creating index '${HEC_INDEX}' (if missing)..."
if ! docker exec "$SPLUNK_CONTAINER" "$SPLUNK_BIN" list index -auth "$AUTH" 2>/dev/null | grep -q "^${HEC_INDEX} "; then
  docker exec "$SPLUNK_CONTAINER" "$SPLUNK_BIN" add index "$HEC_INDEX" -auth "$AUTH"
else
  echo "[bootstrap] Index already exists."
fi

echo "[bootstrap] Creating HEC token (name: orchestra-acme-otel)..."
# Remove stale input with same name so re-runs are idempotent
docker exec "$SPLUNK_CONTAINER" "$SPLUNK_BIN" remove httpevent \
  -name orchestra-acme-otel -auth "$AUTH" 2>/dev/null || true

docker exec "$SPLUNK_CONTAINER" "$SPLUNK_BIN" http-event-collector create -auth "$AUTH" \
  -name orchestra-acme-otel \
  -uri /services/data/inputs/http/orchestra-acme-otel \
  -index "$HEC_INDEX" \
  -sourcetype "$HEC_SOURCETYPE" \
  -token "$HEC_TOKEN"

echo "[bootstrap] Restarting OTel collector to flush HEC retry queue..."
docker compose restart otel_collector >/dev/null 2>&1 || true

echo ""
echo "[bootstrap] Testing HEC from host..."
HTTP_CODE=$(curl -s -o /tmp/acme_hec_test.json -w "%{http_code}" \
  "http://localhost:8088/services/collector/event" \
  -H "Authorization: Splunk ${HEC_TOKEN}" \
  -d "{\"event\":{\"bootstrap\":true,\"sourcetype\":\"${HEC_SOURCETYPE}\"}}") || HTTP_CODE="000"

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "[bootstrap] PASS — HEC returned HTTP 200"
else
  echo "[bootstrap] WARN — HEC test returned HTTP ${HTTP_CODE} (see /tmp/acme_hec_test.json)"
  echo "          Verify token in Splunk: Settings → Data Inputs → HTTP Event Collector"
fi

echo ""
echo "[bootstrap] Next steps:"
echo "  1. Install compliance app: ./scripts/package_splunk_app.sh && see splunk_app/INSTALL.md §4"
echo "  2. Splunk Search: index=${HEC_INDEX} earliest=-15m | stats count"
echo "  3. Open http://localhost:8000 (admin / password from .env)"
