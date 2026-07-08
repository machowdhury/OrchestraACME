#!/usr/bin/env bash
# =============================================================================
# OrchestraACME — Splunk App Packaging Script
# Builds an installable .tar.gz for Splunk Cloud and Splunk Enterprise.
#
# Usage:
#   ./scripts/package_splunk_app.sh
#
# Output:
#   dist/acme_genai_compliance-2.0.0.tar.gz
#
# Install on Splunk Cloud:
#   Apps → Browse more apps → Upload app → select the .tar.gz file
#
# Install on Splunk Enterprise:
#   $SPLUNK_HOME/bin/splunk install app dist/acme_genai_compliance-2.0.0.tar.gz
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${ROOT_DIR}/splunk_app/splunk_compliance_app"
DIST_DIR="${ROOT_DIR}/dist"
APP_ID="acme_genai_compliance"
VERSION="2.3.0"
PACKAGE_NAME="${APP_ID}-${VERSION}"
STAGING_DIR="$(mktemp -d)"
TARGET_DIR="${STAGING_DIR}/${APP_ID}"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Source app not found at ${SRC_DIR}" >&2
  exit 1
fi

echo "[package] Syncing technique playbook lookups from taxonomy..."
python3 "${ROOT_DIR}/scripts/sync_splunk_lookups.py"

echo "[package] Staging ${APP_ID} v${VERSION}..."
mkdir -p "${TARGET_DIR}"
rsync -a \
  --exclude '.DS_Store' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "${SRC_DIR}/" "${TARGET_DIR}/"

mkdir -p "${DIST_DIR}"
OUTPUT="${DIST_DIR}/${PACKAGE_NAME}.tar.gz"

echo "[package] Creating ${OUTPUT}..."
tar -czf "${OUTPUT}" -C "${STAGING_DIR}" "${APP_ID}"

rm -rf "${STAGING_DIR}"

echo "[package] Done."
echo ""
echo "  Installable package: ${OUTPUT}"
echo "  App folder name:     ${APP_ID}"
echo ""
echo "  Splunk Cloud:  Apps → Upload app → ${PACKAGE_NAME}.tar.gz"
echo "  Enterprise:    splunk install app ${OUTPUT}"
echo "  Local Docker:  docker cp ${OUTPUT} acme_splunk:/tmp/ && docker compose exec splunk splunk install app /tmp/${PACKAGE_NAME}.tar.gz -update 1 -auth admin:\$SPLUNK_PASSWORD"
