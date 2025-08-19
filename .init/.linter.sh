#!/bin/bash
cd /home/kavia/workspace/code-generation/cinestream--movie--web-series-streaming-app-96446-96626/Backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

