import os
import shutil
import unittest

from pyDownload import Downloader
from utils import md5


class testDownload(unittest.TestCase):
    TEST_URL_1 = 'http://ovh.net/files/1Mio.dat'
    TEST_URL_2 = 'https://raw.githubusercontent.com/party98/pyDownload/development/README.md'

    def setUp(self):
        os.makedirs('temp')
        os.chdir('temp')

    def tearDown(self):
        os.chdir('..')
        shutil.rmtree('temp')

    def test_Download_without_gzip(self):
        download = Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertFalse(download.is_gzip)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        download.start_download()
        self.assertTrue(os.path.exists('1Mio.dat'))
        self.assertEqual(os.path.getsize('1Mio.dat'), 1048576)
        self.assertEqual(md5('1Mio.dat'), '6cb91af4ed4c60c11613b75cd1fc6116')

    def test_Download_with_gzip(self):
        download = Downloader(url=self.TEST_URL_2, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertTrue(download.is_gzip)
        self.assertEqual(download.file_name, 'README.md')
        download.start_download()
        self.assertTrue(os.path.exists('README.md'))

    def test_ThreadNumChanges(self):
        download = Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        self.assertEqual(download.thread_num, 10)
        self.assertEqual(len(download._range_list), 10)
        download.thread_num = 4
        self.assertEqual(download.thread_num, 4)
        self.assertEqual(len(download._range_list), 4)

    def test_auto_start_download(self):
        download = Downloader(url=self.TEST_URL_1)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        self.assertTrue(os.path.exists('1Mio.dat'))
