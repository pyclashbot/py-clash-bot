"""macOS build script using PyInstaller to create .app bundle and DMG."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

PROJECT_NAME = "py-clash-bot"
AUTHOR = "Matthew Miglio, Martin Miglio"
DESCRIPTION = "Automated Clash Royale"
COPYRIGHT = "2025 Matthew Miglio, Martin Miglio"
ENTRY_POINT = ROOT_DIR / "pyclashbot" / "__main__.py"
ICON_PATH = ROOT_DIR / "assets" / "pixel-pycb.ico"

# Parse --target-version argument
try:
    VERSION = sys.argv[sys.argv.index("--target-version") + 1]
except (ValueError, IndexError):
    VERSION = "v0.0.0"

# Write version file
version_file = ROOT_DIR / "pyclashbot" / "__version__"
if not version_file.exists():
    version_file.touch()
with version_file.open("w", encoding="utf-8") as f:
    f.write(VERSION)

# Clean previous builds
dist_dir = ROOT_DIR / "dist"
build_dir = ROOT_DIR / "build"
spec_file = ROOT_DIR / f"{PROJECT_NAME}.spec"

for path in [dist_dir, build_dir]:
    if path.exists():
        shutil.rmtree(path)
if spec_file.exists():
    spec_file.unlink()

# Data files to bundle
datas = [
    (str(ROOT_DIR / "pyclashbot" / "detection" / "reference_images"), "pyclashbot/detection/reference_images"),
    (str(ROOT_DIR / "assets" / "pixel-pycb.ico"), "assets"),
    (str(version_file), "pyclashbot"),
]

# Build add-data arguments
add_data_args = []
for src, dest in datas:
    add_data_args.extend(["--add-data", f"{src}:{dest}"])

# Run PyInstaller
pyinstaller_args = [
    str(ENTRY_POINT),
    "--name",
    PROJECT_NAME,
    "--windowed",
    "--noconfirm",
    "--clean",
    "--icon",
    str(ICON_PATH),
    "--distpath",
    str(dist_dir),
    "--workpath",
    str(build_dir),
    "--specpath",
    str(ROOT_DIR),
    *add_data_args,
]

print(f"[setup_macos] Building {PROJECT_NAME} version {VERSION}")
print(f"[setup_macos] Running PyInstaller with args: {' '.join(pyinstaller_args)}")

PyInstaller.__main__.run(pyinstaller_args)

# Verify .app was created
app_path = dist_dir / f"{PROJECT_NAME}.app"
if not app_path.exists():
    print(f"[setup_macos] ERROR: {app_path} was not created!")
    sys.exit(1)

print(f"[setup_macos] Successfully created {app_path}")

# Create DMG with Applications shortcut
dmg_name = f"{PROJECT_NAME}-{VERSION}-macos.dmg"
dmg_path = dist_dir / dmg_name
dmg_contents = dist_dir / "dmg_contents"

# Clean and prepare DMG contents folder
if dmg_contents.exists():
    shutil.rmtree(dmg_contents)
dmg_contents.mkdir()

# Copy .app and create Applications symlink
shutil.copytree(app_path, dmg_contents / f"{PROJECT_NAME}.app")
(dmg_contents / "Applications").symlink_to("/Applications")

# Create DMG using hdiutil
print(f"[setup_macos] Creating DMG: {dmg_path}")
subprocess.run(
    [
        "hdiutil",
        "create",
        "-volname",
        PROJECT_NAME,
        "-srcfolder",
        str(dmg_contents),
        "-ov",
        "-format",
        "UDZO",
        str(dmg_path),
    ],
    check=True,
)

# Clean up temporary DMG contents
shutil.rmtree(dmg_contents)

print(f"[setup_macos] Successfully created {dmg_path}")
print("[setup_macos] Build complete!")
