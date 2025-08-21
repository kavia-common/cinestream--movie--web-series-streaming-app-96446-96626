#!/bin/bash
cd /home/kavia/workspace/code-generation/cinestream--movie--web-series-streaming-app-96446-96626/Backend
#!/usr/bin/env bash
set -euo pipefail

# Try to use flake8 if available on PATH; otherwise fall back to python -m flake8
run_flake8() {
  if command -v flake8 >/dev/null 2>&1; then
    flake8
  else
    # Try common python commands
    if command -v python >/dev/null 2>&1; then
      python -m flake8
    elif command -v python3 >/dev/null 2>&1; then
      python3 -m flake8
    else
      echo "flake8 is not installed and no python interpreter found to run 'python -m flake8'." >&2
      exit 1
    fi
  fi
}

# If a venv exists locally, activate it; otherwise continue without activation
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

run_flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

