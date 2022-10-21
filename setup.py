import os
from glob import glob

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

# get github workflow env vars
try:
    version = (os.environ['GIT_TAG_NAME']).replace('v', '')
except KeyError:
    print('Defaulting to 0.0.0')
    version = '0.0.0'

# get files to include in dist
dist_files = [file.replace('pyclashbot/', '')
              for file in glob("pyclashbot/reference_images/*/*.png")]

setup(
    name='py-clash-bot',
    version=version,
    description='Automated Clash Royale',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='clash royale bot',
    author='Matthew Miglio, Martin Miglio',
    url='https://matthewmiglio.github.io/py-clash-bot/',
    download_url='https://matthewmiglio.github.io/py-clash-bot/',
    install_requires=[
        'pillow',
        'opencv-python',
        'keyboard',
        'numpy',
        'ahk',
        'pyautogui',
        'pygetwindow',
        'joblib',
        'tqdm',
        'requests',
        'matplotlib',
        'PySimpleGUI',
        "ahk",
    ],
    packages=['pyclashbot'],
    include_package_data=True,
    package_data={'pyclashbot': dist_files},
    python_requires='>=3.10',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pyclashbot = pyclashbot.__main__:main_gui',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.10',
    ],
)
