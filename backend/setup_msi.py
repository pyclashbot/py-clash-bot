import sys

from cx_Freeze import Executable, setup

product_name = "py-clash-bot"

try:
    version = sys.argv[sys.argv.index("--target-version") + 1]
except ValueError:
    version = "dev"

bdist_msi_options = {
    "upgrade_code": "{494bebef-6fc5-42e5-98c8-d0b2e339750e}",
    "add_to_path": False,
    "initial_target_dir": f"[ProgramFilesFolder]\\{product_name}",
    "summary_data": {
        "author": "Matthew Miglio, Martin Miglio",
        "comments": "A bot for the game Clash of Clans",
        "keywords": "clash of clans bot",
    },
}


# sepccify program as gui so it doesnt open a console (use None for debugging)
base = "Win32GUI"

exe = Executable(
    script="pyclashbot\\__main__.py",
    base=base,
    shortcut_name=f"{product_name} {version}",
    shortcut_dir="DesktopFolder",
    target_name=f"{product_name}.exe",
    copyright="2022 Matthew Miglio",
    icon="..\\docs\\src\\assets\\pixel-pycb.ico",
)

setup(
    name=product_name,
    description="Automated Clash Royale",
    executables=[exe],
    options={
        "bdist_msi": bdist_msi_options,
        "build_exe": {"excludes": ["test", "setuptools"]},
    },
)
