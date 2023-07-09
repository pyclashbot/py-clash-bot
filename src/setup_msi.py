import sys

from cx_Freeze import Executable, setup

PROJECT_NAME = "py-clash-bot"
AUTHOR = "Matthew Miglio, Martin Miglio"
DESCRIPTION = "Automated Clash Royale"
KEYWORDS = "clash of clans bot"
COPYRIGHT = "2023 Matthew Miglio"
ENTRY_POINT = "pyclashbot\\__main__.py"
ICON_PATH = "..\\assets\\pixel-pycb.ico"
GUI = True
UPGRADE_CODE = "{494bebef-6fc5-42e5-98c8-d0b2e339750e}"


try:
    VERSION = sys.argv[sys.argv.index("--target-version") + 1]
except ValueError:
    VERSION = "dev"


build_exe_options = {
    "excludes": ["test", "setuptools"],
    "include_files": ["..\\assets\\pixel-pycb.ico"],
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
