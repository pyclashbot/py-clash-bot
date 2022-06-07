from platform import system
import unittest
from setuptools import sandbox


class CompileTest(unittest.TestCase):
    def test_windows_compile(self):
        if system() == 'Windows':
            sandbox.run_setup('setup_msi.py', ['bdist_msi'])

    def test_wheel_compile(self):
        sandbox.run_setup('setup.py', ['sdist'])
