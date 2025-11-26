#!/usr/bin/env bash
set -e

APP_NAME="ClashBot"
APP_DIR="$PWD/${APP_NAME}.app"

echo "Rebuilding ${APP_NAME}.app in $APP_DIR"

# 1. Remove any old app
rm -rf "$APP_DIR"

# 2. Create bundle structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# 3. Create the launcher executable
cat > "$APP_DIR/Contents/MacOS/launcher" << 'LAUNCHER_EOF'
#!/usr/bin/env bash
set -euo pipefail

# This script runs when the user opens ClashBot.app

# Resolve the app bundle's Contents dir
CONTENTS_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Repo root is the parent folder of the .app
REPO_ROOT="$(cd "$CONTENTS_DIR/.." && pwd)"

# Go to repo root and run your mac script
cd "$REPO_ROOT"
cd ..
exec ./scripts/run_mac.sh
LAUNCHER_EOF

chmod +x "$APP_DIR/Contents/MacOS/launcher"

# 4. Create a minimal Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>CFBundleName</key>
    <string>PY-ClashBot</string>

    <key>CFBundleDisplayName</key>
    <string>PY-ClashBot</string>

    <key>CFBundleIdentifier</key>
    <string>com.py-clash-bot.clashbot</string>

    <key>CFBundleVersion</key>
    <string>1.0</string>

    <key>CFBundleShortVersionString</key>
    <string>1.0</string>

    <key>CFBundleExecutable</key>
    <string>launcher</string>

    <key>CFBundlePackageType</key>
    <string>APPL</string>

    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>

    <key>LSBackgroundOnly</key>
    <false/>
  </dict>
</plist>
PLIST_EOF

echo "Done. You should now have ${APP_NAME}.app"
