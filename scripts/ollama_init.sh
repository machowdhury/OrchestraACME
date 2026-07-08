#!/bin/bash
# =============================================================================
# OrchestraACME — Ollama Container Initialisation Script
# Starts the Ollama server, waits for readiness, then pulls llama3.2:1b
# =============================================================================
set -e

MODEL="${OLLAMA_MODEL:-llama3.2:1b}"

echo "[ollama_init] Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

echo "[ollama_init] Waiting for Ollama API to become ready..."
MAX_WAIT=120
WAITED=0
until curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; do
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "[ollama_init] ERROR: Ollama did not start within ${MAX_WAIT}s"
        exit 1
    fi
    sleep 2
    WAITED=$((WAITED + 2))
done
echo "[ollama_init] Ollama API ready after ${WAITED}s"

# Check if model is already pulled (cached in ollama_models volume)
if ollama list | grep -q "$MODEL"; then
    echo "[ollama_init] Model '$MODEL' already present — skipping pull"
else
    echo "[ollama_init] Pulling model '$MODEL'..."
    ollama pull "$MODEL"
    echo "[ollama_init] Model '$MODEL' pull complete"
fi

echo "[ollama_init] Ollama ready. Handing off to server process..."
wait $OLLAMA_PID
