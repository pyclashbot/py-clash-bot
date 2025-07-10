import sys
from pathlib import Path

from cx_Freeze import Executable, setup

ROOT_DIR = Path(__file__).parent.parent

PROJECT_NAME = "py-clash-bot"
AUTHOR = "Matthew Miglio, Martin Miglio"
DESCRIPTION = "Automated Clash Royale"
KEYWORDS = "clash of clans bot"
COPYRIGHT = "2023 Matthew Miglio"
ENTRY_POINT = ROOT_DIR / "pyclashbot" / "__main__.py"
ICON_PATH = ROOT_DIR / "assets" / "pixel-pycb.ico"
GUI = True
UPGRADE_CODE = "{494bebef-6fc5-42e5-98c8-d0b2e339750e}"


try:
    VERSION = sys.argv[sys.argv.index("--target-version") + 1]
except (ValueError, IndexError):
    VERSION = "v0.0.0"

version_file = ROOT_DIR / "pyclashbot" / "__version__"
if not version_file.exists():
    version_file.touch()
with version_file.open("w", encoding="utf-8") as f:
    f.write(VERSION)


build_exe_options = {
    "excludes": ["test", "setuptools"],
    "include_files": [
        ROOT_DIR / "assets" / "pixel-pycb.ico",
        ROOT_DIR / "pyclashbot" / "detection" / "reference_images",
        ROOT_DIR / "pyclashbot" / "__version__",
    ],
    "include_msvcr": True,
}

bdist_msi_options = {
    "upgrade_code": UPGRADE_CODE,
    "add_to_path": False,
    "initial_target_dir": f"[ProgramFilesFolder]\\{PROJECT_NAME}",
    "summary_data": {
        "author": AUTHOR,
        "comments": DESCRIPTION,
        "keywords": KEYWORDS,
    },
}

exe = Executable(
    script=ENTRY_POINT,
    base="Win32GUI" if GUI else None,
    uac_admin=True,
    shortcut_name=f"{PROJECT_NAME} {VERSION}",
    shortcut_dir="DesktopFolder",
    target_name=f"{PROJECT_NAME}.exe",
    copyright=COPYRIGHT,
    icon=ICON_PATH,
)

setup(
    name=PROJECT_NAME,
    description=DESCRIPTION,
    executables=[exe],
    options={
        "bdist_msi": bdist_msi_options,
        "build_exe": build_exe_options,
    },
)
