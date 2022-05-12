import sys
import os
from cx_Freeze import setup, Executable




# get github workflow env vars
try:
    version = os.environ['RELEASE_VERSION']
except KeyError:
    print('Defaulting to v0.0.0')
    version = 'v0.0.0'

product_name = f'py-clash-bot {version}'

bdist_msi_options = {
    'upgrade_code': '{494bebef-6fc5-42e5-98c8-d0b2e339750e}',
    'add_to_path': False,
    'initial_target_dir': f'[ProgramFilesFolder]\\{product_name}',
}

dependencies = ['random', 'time', 'PIL', 'cv2', 'keyboard',
                'matplotlib', 'numpy', 'pyautogui', 'pygetwindow', 'os', 'utils']

build_exe_options = {
    'includes': dependencies,
    'include_files': ['reference_images/'],
}


# GUI applications require a different base on Windows
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

exe = Executable(
    script='test7.py',
    base=base,
    shortcut_name=product_name,
    shortcut_dir="DesktopFolder",
)

setup(
    name=product_name,
    version=version.replace('v', ''),
    description='blah',
    executables=[exe],
    options={
        'bdist_msi': bdist_msi_options,
        'build_exe': build_exe_options
    }
)
