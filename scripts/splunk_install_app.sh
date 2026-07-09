#!/usr/bin/env bash
# =============================================================================
# OrchestraACME — Install GenAI Compliance Splunk app into local Docker Splunk
# Runs splunk CLI as the splunk user (not root) to avoid permission errors.
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
SPLUNK_BIN="/opt/splunk/bin/splunk"
AUTH="admin:${SPLUNK_PASSWORD}"

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

BASENAME="$(basename "$TARBALL")"
REMOTE="/tmp/${BASENAME}"

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

echo "[install] Copying ${BASENAME} into container..."
docker cp "$TARBALL" "${SPLUNK_CONTAINER}:${REMOTE}"

echo "[install] Installing app as splunk user..."
docker exec -u splunk "$SPLUNK_CONTAINER" "$SPLUNK_BIN" install app \
  "$REMOTE" -update 1 -auth "$AUTH"

echo "[install] Restarting Splunk..."
docker exec -u splunk "$SPLUNK_CONTAINER" "$SPLUNK_BIN" restart

echo ""
echo "[install] Done. Open http://localhost:8000 → GenAI Compliance Monitor"
echo "  Login: admin / (password from .env SPLUNK_PASSWORD)"
