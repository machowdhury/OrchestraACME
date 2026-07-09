#!/usr/bin/env bash
# =============================================================================
# OrchestraACME — Install GenAI Compliance Splunk app into local Docker Splunk
# Copies app into /opt/splunk/etc/apps (reliable in containers). Repairs
# ownership if splunk CLI was previously run as root.
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

SPLUNK_PASSWORD="${SPLUNK_PASSWORD:-ACMEPassword2026!}"
SPLUNK_CONTAINER="${SPLUNK_CONTAINER:-acme_splunk}"
APP_ID="${SPLUNK_APP_ID:-acme_genai_compliance}"
SPLUNK_BIN="/opt/splunk/bin/splunk"
AUTH="admin:${SPLUNK_PASSWORD}"
APPS_DIR="/opt/splunk/etc/apps/${APP_ID}"

# Optional arg: path to tarball; otherwise package latest
TARBALL="${1:-}"

if [[ -z "$TARBALL" ]]; then
  echo "[install] Packaging Splunk app..."
  ./scripts/package_splunk_app.sh
  TARBALL="$(ls -1 dist/acme_genai_compliance-*.tar.gz 2>/dev/null | sort -V | tail -1)"
fi

if [[ ! -f "$TARBALL" ]]; then
  echo "[install] ERROR: tarball not found: ${TARBALL}" >&2
  echo "  Run: ./scripts/package_splunk_app.sh" >&2
  exit 1
fi

echo "[install] Waiting for Splunk (${SPLUNK_CONTAINER})..."
for i in $(seq 1 60); do
  if docker exec "$SPLUNK_CONTAINER" curl -sfk -u "$AUTH" \
      "https://127.0.0.1:8089/services/server/info" >/dev/null 2>&1; then
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "[install] ERROR: Splunk not ready. Check: docker compose logs splunk" >&2
    exit 1
  fi
  sleep 5
done

echo "[install] Repairing Splunk filesystem ownership (fixes prior root CLI runs)..."
docker exec -u root "$SPLUNK_CONTAINER" bash -c "
  mkdir -p /opt/splunk/var/run/splunk/bundle_tmp
  mkdir -p /opt/splunk/var/log/splunk /opt/splunk/var/log/introspection
  mkdir -p /opt/splunk/var/log/watchdog /opt/splunk/var/log/client_events
  chown -R splunk:splunk /opt/splunk/etc /opt/splunk/var
"

STAGING="$(mktemp -d)"
trap 'rm -rf "${STAGING}"' EXIT

echo "[install] Extracting $(basename "$TARBALL")..."
tar -xzf "$TARBALL" -C "$STAGING"
if [[ ! -d "${STAGING}/${APP_ID}" ]]; then
  echo "[install] ERROR: expected folder '${APP_ID}/' inside tarball" >&2
  exit 1
fi

echo "[install] Deploying to ${APPS_DIR}..."
docker exec -u root "$SPLUNK_CONTAINER" rm -rf "${APPS_DIR}"
docker cp "${STAGING}/${APP_ID}" "${SPLUNK_CONTAINER}:${APPS_DIR}"
docker exec -u root "$SPLUNK_CONTAINER" chown -R splunk:splunk "${APPS_DIR}"

echo "[install] Restarting Splunk..."
docker exec -u splunk "$SPLUNK_CONTAINER" "$SPLUNK_BIN" restart

echo ""
echo "[install] Done. Open http://localhost:8000 → GenAI Compliance Monitor"
echo "  Login: admin / (password from .env SPLUNK_PASSWORD)"
