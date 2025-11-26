#!/usr/bin/env bash
set -e

# Always run from repo root
cd "$(dirname "$0")/.."

VENV_DIR=".venv"
VENV_PY="$VENV_DIR/bin/python"

# 1. Check system Python (for creating the venv)
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3.12+ from python.org or Homebrew."
  exit 1
fi

# 2. Always recreate venv from scratch
if [ -d "$VENV_DIR" ]; then
  echo "Removing existing virtualenv in .venv..."
  rm -rf "$VENV_DIR"
  rm -rf %appdata%
  rm -rf build
fi

echo "Creating virtualenv in .venv..."
python3 -m venv "$VENV_DIR"

# Use the venv's Python directly (no 'activate' needed)
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install .
"$VENV_PY" -m pip install pyobjc-core pyobjc-framework-Quartz

# 3. Make sure adb exists
if ! command -v adb >/dev/null 2>&1; then
  echo "adb not found. Install Android platform-tools, for example:"
  echo "  brew install android-platform-tools"
  exit 1
fi

# 4. Run the bot using the venv's Python
exec "$VENV_PY" -m pyclashbot