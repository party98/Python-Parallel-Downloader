# -*- coding: utf-8 -*-
import random
from itertools import chain
from queue import Queue
from threading import Thread

from . import Downloader
from .status import DownloadStatus


class DownloadQueue(object):
    def __init__(self, downloads, max_active_downloads=5, wait_for_download=False, auto_start=True):
        self._status = DownloadStatus.INITIALIZING
        self._downloads = self._init_download(downloads)
        self._active_downloads = max_active_downloads
        self._download_queue = Queue()
        for download_id, download_obj in chain(self._downloads.items(), [('STOP', 'STOP')] * self._active_downloads):
            self._download_queue.put((download_id, download_obj))
        self._download_manager = Thread(target=self._manager_worker)
        self._status = DownloadStatus.READY
        if auto_start:
            self._status = DownloadStatus.STARTED
            self._download_manager.start()
            if wait_for_download:
                self._download_manager.join()

    @staticmethod
    def _init_download(downloads):
        download_ids = {}
        for download in downloads:
            download.update({'auto_start': False})
            download_ids[random.randint(
                100000, 999999)] = Downloader(**download)
        return download_ids

    def _manager_worker(self):
        self._status = DownloadStatus.RUNNING
        threads = []
        for _ in range(self._active_downloads):
            thread = Thread(target=self._download_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        self._status = DownloadStatus.FINISHED

    def _download_worker(self):
        while True:
            download_id, download_obj = self._download_queue.get()
            if download_id == 'STOP':
                return
            download_obj.start_download(wait_for_download=True)

    def start_download(self, wait_for_download=False):
        self._download_manager.start()
        if wait_for_download:
            self._download_manager.join()

    def get_download(self, download_id):
        return self._downloads.get(download_id)

    def get_downloads(self):
        return self._downloads

    @property
    def status(self):
        return self._status
