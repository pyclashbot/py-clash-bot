import unittest
from platform import system

from setuptools import sandbox


class CompileTest(unittest.TestCase):
    def test_msi_dist_compile(self):
        if system() == "Windows":
            sandbox.run_setup("setup_msi.py", ["bdist_msi"])


if __name__ == "__main__":
    unittest.main()
