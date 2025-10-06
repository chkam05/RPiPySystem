#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Generate project_context.md using ./gpt/context_generator.py.
# -----------------------------------------------------------------------------

set -Eeuo pipefail

# Work from project root (parent of ./.gpt)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"

cd "$PROJECT_ROOT"

# Activate Python Virtual Environment
# -----------------------------------------------------------------------------
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "[$APP_NAME] ERR: Missing .venv. Run ./scripts/install.sh first." >&2
    exit 1
fi
# -----------------------------------------------------------------------------

# Configuration
# -----------------------------------------------------------------------------
GENERATOR_SCRIPT="$PROJECT_ROOT/.gpt/context_generator.py"
OUT_FILE="${OUT_FILE:-$PROJECT_ROOT/project_context.md}"
MAX_DEPTH="${MAX_DEPTH:-3}"
# -----------------------------------------------------------------------------

if [ -f "$GENERATOR_SCRIPT" ]; then
    echo "[$APP_NAME] Starting ChatGPT context file generation script ..."
    python "$GENERATOR_SCRIPT" \
        --root "$PROJECT_ROOT" \
        --out "$OUT_FILE" \
        --max-depth "$MAX_DEPTH"

    echo "[$APP_NAME] Context file generation finished: $OUT_FILE"
else
    echo "[$APP_NAME] ERR: ChatGPT context generation script not found at: ${PY_SCRIPT}" >&2
    exit 1
fi