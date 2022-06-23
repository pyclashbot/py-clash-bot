import os

from cx_Freeze import Executable, setup

# get github workflow env vars
try:
    version = os.environ['GIT_TAG_NAME']
except KeyError:
    print('Defaulting to v0.0.0')
    version = 'v0.0.0'

product_name = 'py-clash-bot'

bdist_msi_options = {
    'upgrade_code': '{494bebef-6fc5-42e5-98c8-d0b2e339750e}',
    'add_to_path': False,
    'initial_target_dir': f'[ProgramFilesFolder]\\{product_name}',
}

dependencies = [
    'PIL',
    'cv2',
    'keyboard',
    'numpy',
    'pyautogui',
    'pygetwindow',
    'joblib',
    'tqdm',
    'requests',
    'matplotlib'
]

build_exe_options = {
    'includes': dependencies,
    'include_files': [
        'pyclashbot/reference_images/',
        'README.md',
        'pyclashbot/cache/'
    ]}


# GUI applications require a different base on Windows
base = None
# if sys.platform == 'win32':
#    base = 'Win32GUI'

exe = Executable(
    script='pyclashbot\\__main__.py',
    base=base,
    shortcut_name=f"{product_name} {version}",
    shortcut_dir="DesktopFolder",
)

setup(
    name=product_name,
    version=version.replace('v', ''),
    description='Automated Clash Royale',
    executables=[exe],
    options={
        'bdist_msi': bdist_msi_options,
        'build_exe': build_exe_options
    }
)
