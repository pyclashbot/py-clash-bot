#!/usr/bin/env bash
set -euo pipefail

# Change to the clashapp directory (folder that contains buildenv, run_bot.py, etc.)
cd "$(dirname "$0")"

echo "[ClashBot macOS] Using virtualenv: buildenv"

# 1. Make sure the venv exists
if [ ! -d "buildenv" ]; then
  echo "Error: buildenv virtualenv not found in $(pwd)"
  echo "Create it first, for example:"
  echo "  python3 -m venv buildenv"
  echo "  source buildenv/bin/activate"
  echo "  pip install pyinstaller"
  echo "  pip install ."
  exit 1
fi

# 2. Activate the venv
# shellcheck disable=SC1091
source buildenv/bin/activate

# 3. Make sure pyinstaller is available inside the venv
if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "Error: pyinstaller is not installed in buildenv."
  echo "Run: source buildenv/bin/activate && pip install pyinstaller"
  exit 1
fi

echo "[ClashBot macOS] Building ClashBot.app with PyInstaller"

# 4. Optional: clean old build artifacts
rm -rf build dist ClashBot.spec

# 5. Run PyInstaller
pyinstaller \
  --windowed \
  --name "ClashBot" \
  --icon clashbot.icns \
  --hidden-import pyclashbot \
  --hidden-import pyclashbot.__main__ \
  --add-data "pyclashbot/detection/reference_images:pyclashbot/detection/reference_images" \
  --add-data "platform-tools:platform-tools" \
  --add-data "pyclashbot/interface/assets:pyclashbot/interface/assets" \
  --add-data "assets:assets" \
  run_bot.py

echo ""
echo "[ClashBot macOS] Build complete."
echo "You should now have: dist/ClashBot.app"