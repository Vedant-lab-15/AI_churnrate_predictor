#!/usr/bin/env bash
# run.sh — sets up the environment and launches EasyAnalytics

set -e

VENV_DIR=".venv"

echo "──────────────────────────────────────"
echo "  EasyAnalytics — starting up"
echo "──────────────────────────────────────"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "→ Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Activate it
source "$VENV_DIR/bin/activate"

# Install / upgrade dependencies
echo "→ Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "→ Launching app at http://localhost:8501"
echo "   Press Ctrl+C to stop."
echo "──────────────────────────────────────"

streamlit run app.py
