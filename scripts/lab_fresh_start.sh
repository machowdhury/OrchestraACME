#!/usr/bin/env bash
# =============================================================================
# OrchestraACME — Full lab reset (containers, volumes, .env, Splunk setup)
#
# Usage:
#   ./scripts/lab_fresh_start.sh          # prompts for confirmation
#   ./scripts/lab_fresh_start.sh --yes    # no prompt (CI / scripted VMs)
#
# What this removes:
#   - All OrchestraACME containers
#   - Docker volumes (Ollama model cache, shared telemetry)
#   - Recreates .env from .env.example (backs up existing .env if present)
#
# What this does NOT remove:
#   - Git clone / source code
#   - dist/*.tar.gz you built locally
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ASSUME_YES=false
for arg in "$@"; do
  case "$arg" in
    -y|--yes) ASSUME_YES=true ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg (use --yes or --help)" >&2
      exit 1
      ;;
  esac
done

if [[ "$ASSUME_YES" != true ]]; then
  echo "This will DESTROY all lab containers and volumes (including Ollama model)."
  echo "Repo source code is kept. .env is recreated from .env.example."
  read -r -p "Type 'yes' to continue: " confirm
  if [[ "$confirm" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo "[fresh] Stopping and removing containers + volumes..."
docker compose --profile local down -v --remove-orphans 2>/dev/null || \
  docker compose down -v --remove-orphans 2>/dev/null || true

# Force-remove named containers if compose left them behind
for c in acme_splunk acme_ollama acme_banking_app acme_attack_panel acme_otel_collector; do
  docker rm -f "$c" 2>/dev/null || true
done

echo "[fresh] Recreating .env..."
if [[ -f .env ]]; then
  cp .env ".env.bak.$(date +%Y%m%d%H%M%S)"
  echo "[fresh] Backed up existing .env"
fi
cp .env.example .env

echo "[fresh] Building and starting stack (5–15 min first boot)..."
docker compose --profile local up --build -d

echo "[fresh] Waiting for Ollama model pull (up to 10 min)..."
for i in $(seq 1 60); do
  if docker compose exec -T ollama ollama list 2>/dev/null | grep -q "llama"; then
    echo "[fresh] Ollama model ready."
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "[fresh] WARN: Ollama still pulling — check: docker compose logs -f ollama"
  fi
  sleep 10
done

echo "[fresh] Waiting for Splunk Web (up to 8 min)..."
for i in $(seq 1 48); do
  if curl -sf "http://localhost:8000/en-US/account/login" >/dev/null 2>&1; then
    echo "[fresh] Splunk Web is up."
    break
  fi
  if [[ "$i" -eq 48 ]]; then
    echo "[fresh] WARN: Splunk slow — check: docker compose logs -f splunk"
  fi
  sleep 10
done

echo "[fresh] Bootstrapping Splunk HEC + index..."
chmod +x scripts/splunk_local_bootstrap.sh scripts/splunk_install_app.sh
./scripts/splunk_local_bootstrap.sh

echo "[fresh] Installing Splunk compliance app..."
./scripts/splunk_install_app.sh

echo ""
echo "=============================================="
echo "  OrchestraACME fresh lab is ready"
echo "=============================================="
echo ""
echo "  Banking app:   http://localhost:5000"
echo "  Attack panel:  http://localhost:5001"
echo "  Splunk Web:    http://localhost:8000"
echo "  Splunk login:  admin / ACMEPassword2026!"
echo ""
echo "  Verify:"
echo "    curl -s http://localhost:5000/health | python3 -m json.tool"
echo "    # Splunk: index=acme_agentic_telemetry earliest=-15m | stats count"
echo ""
