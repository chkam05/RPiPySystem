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

# Provide files (space or newline separated) to embed fully in the MD.
# EXTRA_MD_FILES="${EXTRA_MD_FILES:-}"
EXTRA_MD_FILES="./launch.sh\
    ./supervisord.conf \
    ./.env.example"
# -----------------------------------------------------------------------------

# Build a sanitized array of absolute paths for --extra
# -----------------------------------------------------------------------------
EXTRA_ARGS=()
if [ -n "$EXTRA_MD_FILES" ]; then
    # shellcheck disable=SC2206
    EXTRA_LIST=($EXTRA_MD_FILES)
    for p in "${EXTRA_LIST[@]}"; do
        if [ -e "$p" ]; then
            EXTRA_ARGS+=("$(realpath -m "$p")")
        else
            echo "[$APP_NAME] WARN: extra file not found: $p" >&2
        fi
    done
fi
# -----------------------------------------------------------------------------

if [ -f "$GENERATOR_SCRIPT" ]; then
    echo "[$APP_NAME] Starting ChatGPT context file generation script ..."

    PY_ARGS=( --root "$PROJECT_ROOT" --out "$OUT_FILE" --max-depth "$MAX_DEPTH" )

    if [ ${#EXTRA_ARGS[@]} -gt 0 ]; then
        PY_ARGS+=( --extra "${EXTRA_ARGS[@]}" )
    fi
    
    python "$GENERATOR_SCRIPT" "${PY_ARGS[@]}"

    echo "[$APP_NAME] Context file generation finished: $OUT_FILE"
else
    echo "[$APP_NAME] ERR: ChatGPT context generation script not found at: ${PY_SCRIPT}" >&2
    exit 1
fi