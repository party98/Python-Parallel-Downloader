import time
from itertools import chain
from queue import Queue
from threading import Thread

import requests

from .base_downloader import BaseDownloader
from .status import DownloadStatus


class ThreadDownloader(BaseDownloader):
    def __init__(self, *args, **kwargs):
        self._paused = False
        self._bytes_downloaded = 0
        super().__init__(*args, **kwargs)

    @property
    def bytes_downloaded(self):
        return self._bytes_downloaded

    @property
    def is_paused(self):
        return self._paused

    def pause(self):
        super().pause()
        if self._running:
            self._paused = True

    def resume(self):
        if self._running and self._paused:
            self._paused = False

    def _download_worker(self, range_start=0, range_end=None):
        while True:
            data = self._queue.get()
            if data == 'STOP':
                return
            range_start, range_end = data
            filename = self._get_filename()
            if range_start is not None and range_end is not None:
                header = {"Range": "bytes=%s-%s" % (range_start, range_end)}
            else:
                header = {}
            with requests.get(url=self._url, stream=True, headers=header) as r:
                with open("%s.temp" % filename, "rb+") as f:
                    pos = range_start or 0
                    i = 0
                    for chunk in r.raw.stream(amt=self._chunk_size):
                        i += 1
                        while self._paused:
                            time.sleep(1)
                        if chunk:
                            f.seek(pos)
                            f.write(chunk)
                            self._bytes_downloaded += len(chunk)
                            pos += len(chunk)

    def download_manager(self):
        super().download_manager()
        self._queue = Queue()
        for i in chain(self._range_iterator, ['STOP'] * self._worker_num):
            self._queue.put(i)

        for _ in range(self._worker_num):
            thread = Thread(
                target=self._download_worker,
            )
            self.running_workers.append(thread)
            thread.start()

        for thread in self.running_workers:
            thread.join()
        self.uncompress_if_gzip()
        self._running = False
        self._status = DownloadStatus.FINISHED
