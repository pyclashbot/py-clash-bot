"""Versioning for the program"""
from os.path import exists, isfile, join, pardir

VERSION_FILE = join(pardir, "__version__")
VERSION = "dev"

# use exists to check if the file exists
if exists(VERSION_FILE) and isfile(VERSION_FILE):
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        VERSION = f.read().strip()

__version__ = VERSION

del VERSION_FILE, VERSION

if __name__ == "__main__":
    print(__version__)
