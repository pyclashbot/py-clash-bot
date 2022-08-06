import unittest
from platform import system

from setuptools import sandbox


class CompileTest(unittest.TestCase):
    def test_msi_dist_compile(self):
        if system() == 'Windows':
            sandbox.run_setup('setup_msi.py', ['bdist_msi'])

    def test_wheel_dist_compile(self):
        sandbox.run_setup('setup.py', ['bdist_wheel'])

    def test_source_dist_compile(self):
        sandbox.run_setup('setup.py', ['sdist'])
