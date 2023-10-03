import unittest
from platform import system
from os.path import dirname, join, pardir

from setuptools import sandbox


class CompileTest(unittest.TestCase):
    def test_msi_dist_compile(self):
        if system() == "Windows":
            setup_file = join(dirname(__file__), pardir, "setup_msi.py")
            sandbox.run_setup(setup_file, ["bdist_msi"])


if __name__ == "__main__":
    unittest.main()
