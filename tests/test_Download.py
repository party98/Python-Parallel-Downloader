import os
import shutil
import time
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

    def test_NumSplitChanges(self):
        download = Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        self.assertEqual(download.num_splits, 10)
        self.assertEqual(len(download._range_list), 10)
        download.num_splits = 4
        self.assertEqual(download.num_splits, 4)
        self.assertEqual(len(download._range_list), 4)

    def test_auto_start_download_1(self):
        download = Downloader(url=self.TEST_URL_1)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        self.assertTrue(os.path.exists('1Mio.dat'))

    def test_auto_start_download_2(self):
        download = Downloader(url=self.TEST_URL_1, wait_for_download=False)

        self.assertTrue(download.is_running)
        while(download.is_running):
            time.sleep(1)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        self.assertTrue(os.path.exists('1Mio.dat'))

    def test_Download_pause_and_resume(self):
        download = Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        download.pause()
        self.assertFalse(download._paused)
        download.resume()
        self.assertFalse(download._paused)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        download.start_download(wait_for_download=False)
        self.assertTrue(download.is_running)
        download.pause()
        time.sleep(0.2)
        self.assertTrue(download._paused)
        download.resume()
        self.assertFalse(download._paused)
        while download.is_running:
            time.sleep(1)
        self.assertTrue(os.path.exists('1Mio.dat'))
        self.assertEqual(os.path.getsize('1Mio.dat'), 1048576)
        self.assertEqual(md5('1Mio.dat'), '6cb91af4ed4c60c11613b75cd1fc6116')
