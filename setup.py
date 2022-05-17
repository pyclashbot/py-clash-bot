from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='py-clash-bot',
    version='0.2.0',
    description='Automated Clash Royale',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='clash royale bot',
    author='Matthew Miglio, Martin Miglio',
    url='https://github.com/matthewmiglio/py-clash-bot',
    download_url='https://github.com/matthewmiglio/py-clash-bot/releases',
    install_requires=[
        'pillow',
        'opencv-python',
        'keyboard',
        'matplotlib',
        'numpy',
        'pyautogui',
        'pygetwindow',
        'joblib'
    ],
    packages=['pyclashbot'],
    include_package_data=True,
    python_requires='>=3',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pyclashbot = pyclashbot.__main__:main_loop',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.10',
    ],
)
