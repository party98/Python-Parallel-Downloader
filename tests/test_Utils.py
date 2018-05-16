import os
import shutil
import unittest

from pyDownload import utils


class testREADME(unittest.TestCase):
    def setUp(self):
        os.makedirs('temp')
        os.chdir('temp')

    def tearDown(self):
        os.chdir('..')
        shutil.rmtree('temp')

    def test_create_file(self):
        utils.create_file('test_file')
        self.assertTrue(os.path.exists('test_file'))

    def test_int_or_none(self):
        self.assertIsNone(utils.int_or_none('sa'))
        self.assertEqual(utils.int_or_none('1'), 1)
        self.assertEqual(utils.int_or_none(1.1), 1)
        self.assertEqual(utils.int_or_none(.1), 0)

    def test_head_request(self):
        utils.make_head_req('https://google.com')
