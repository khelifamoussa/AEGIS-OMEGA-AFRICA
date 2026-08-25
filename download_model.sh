#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="model"
MODEL_FILE="${MODEL_DIR}/Qwen3-4B-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf?download=true"

mkdir -p "${MODEL_DIR}"

if [ -s "${MODEL_FILE}" ]; then
  echo "Model already exists: ${MODEL_FILE}"
  exit 0
fi

echo "Downloading Qwen3-4B Q4_K_M GGUF..."
if command -v curl >/dev/null 2>&1; then
  curl -L --fail --retry 3 --retry-delay 2 -o "${MODEL_FILE}.part" "${MODEL_URL}"
elif command -v wget >/dev/null 2>&1; then
  wget -O "${MODEL_FILE}.part" "${MODEL_URL}"
else
  echo "ERROR: curl or wget is required." >&2
  exit 1
fi

mv "${MODEL_FILE}.part" "${MODEL_FILE}"

if [ ! -s "${MODEL_FILE}" ]; then
  echo "ERROR: Downloaded model is missing or empty." >&2
  exit 1
fi

echo "Model ready: ${MODEL_FILE}"
