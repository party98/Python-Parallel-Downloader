import os
import re
import subprocess
import unittest

from utils import extract

code_blocks = []


class testREADME(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('README.md') as f:
            code_blocks.extend(extract(f, filter='python'))
        with open('README.md') as f:
            cls.readme = f.read()

    def setUp(self):
        os.makedirs('temp')
        os.chdir('temp')

    def tearDown(self):
        os.chdir('..')
        os.rmdir('temp')

    def test_Readme(self):
        for code_block in code_blocks:
            compile(code_block[0], 'random.py', mode='exec')

    def test_branch(self):
        current_branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf8')
        urls = re.findall(r'\(https?.*?\)', self.readme)
        for url in urls:
            if 'branch' in url:
                self.assertIn(current_branch, url)
