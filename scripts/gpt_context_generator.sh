#!/usr/bin/env bash
set -euo pipefail

# Change to the project root (one level up from ./scripts)
cd "$(dirname "$0")/.."

# Ensure virtual environment is activated if it exists
if [ -d ".venv" ]; then
  echo "[generate_context] Activating virtual environment..."
  source .venv/bin/activate
fi

# Paths
PY_SCRIPT="./utils/gpt_context_generator.py"
OUT_FILE="./project_context.md"

# Check if script exists
if [ ! -f "$PY_SCRIPT" ]; then
  echo "[generate_context] ERROR: $PY_SCRIPT not found!"
  exit 1
fi

# Run generator
echo "[generate_context] Generating project context..."
python "$PY_SCRIPT" \
  --root . \
  --out "$OUT_FILE" \
  --max-depth 3

echo "[generate_context] Done."
echo "Output saved to: $OUT_FILE"