import os
import shutil
import time
import unittest

import pyDownload


class testPropChange(unittest.TestCase):
    TEST_URL_1 = 'http://ovh.net/files/1Mio.dat'
    TEST_URL_2 = 'http://ovh.net/files/1Mb.dat'

    @classmethod
    def setUpClass(cls):
        os.mkdir('temp')
        os.chdir('temp')

    @classmethod
    def tearDownClass(cls):
        os.chdir('..')
        shutil.rmtree('temp')

    def test_url_change(self):
        downloader = pyDownload.Downloader(
            url=self.TEST_URL_1, auto_start=False)
        init_url = downloader.download_url
        init_size = downloader.download_size
        init_filename = downloader.file_name
        init_range_list = downloader._range_list
        downloader.download_url = self.TEST_URL_2
        self.assertNotEqual(init_size, downloader.download_size)
        self.assertNotEqual(init_filename, downloader.file_name)
        self.assertNotEqual(init_range_list, downloader._range_list)
        self.assertNotEqual(init_url, downloader.download_url)

    def test_thread_num_changes(self):
        download = pyDownload.Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        self.assertEqual(download.download_size, 1048576)
        self.assertEqual(download.thread_num, 10)
        self.assertEqual(len(download._range_list), 10)
        download.thread_num = 4
        self.assertEqual(download.thread_num, 4)
        self.assertEqual(len(download._range_list), 4)

    def test_filename_changes(self):
        download = pyDownload.Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertEqual(download.file_name, '1Mio.dat')
        download.file_name = 'abc.dat'
        self.assertEqual(download.file_name, 'abc.dat')

    def test_chunk_size_changes(self):
        download = pyDownload.Downloader(url=self.TEST_URL_1, auto_start=False)
        self.assertFalse(download.is_running)
        self.assertEqual(download.chunk_size, 1024)
        download.chunk_size = 2048
        self.assertEqual(download.chunk_size, 2048)

    def test_bytes_downloaded_change(self):
        download = pyDownload.Downloader(
            url=self.TEST_URL_1, auto_start=False, wait_for_download=False)
        self.assertFalse(download.is_running)
        self.assertEqual(download.bytes_downloaded, 0)
        download.start_download(wait_for_download=False)
        while download.is_running:
            time.sleep(0.5)
        self.assertFalse(download.is_running)
        self.assertEqual(download.bytes_downloaded, download.download_size)
        os.remove(download.file_name)

    def test_misc_changes(self):
        download = pyDownload.Downloader(
            url=self.TEST_URL_1, auto_start=False, wait_for_download=False, multithreaded=True)
        self.assertTrue(download.multithreaded)
        self.assertFalse(download.wait_for_download)
        download.start_download(wait_for_download=False)
        download.multithreaded = False
        self.assertTrue(download.is_running)
        self.assertTrue(download.multithreaded)
        download.wait_for_download = True
        self.assertFalse(download.wait_for_download)
        while download.is_running:
            time.sleep(0.5)
        os.remove(download.file_name)
