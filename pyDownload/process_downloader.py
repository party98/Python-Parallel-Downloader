import itertools
import time
from multiprocessing import Lock, Process, Queue, Value

import requests

from .base_downloader import BaseDownloader
from .status import DownloadStatus


class ProcessDownloader(BaseDownloader):
    def __init__(self, *args, **kwargs):
        self._paused = Value('i', 0)
        self._bytes_downloaded = Value('i', 0)
        super().__init__(*args, **kwargs)

    @property
    def bytes_downloaded(self):
        return self._bytes_downloaded.value

    @property
    def is_paused(self):
        return bool(self._paused.value)

    def pause(self):
        super().pause()
        if self._running:
            self._paused.value = int(True)

    def resume(self):
        if self._running and bool(self._paused.value):
            self._paused.value = int(False)

    @staticmethod
    def _download_worker(queue, bytes_downloaded, lock, is_pause):
        while True:
            data = queue.get()
            url, filename, chunk_size, range_start, range_end = data
            if range_start == 'STOP':
                return
            if range_start is not None and range_end is not None:
                header = {"Range": "bytes=%s-%s" % (range_start, range_end)}
            else:
                header = {}
            with requests.get(url=url, stream=True, headers=header) as r:
                with open("%s.temp" % filename, "rb+") as f:
                    pos = range_start or 0
                    i = 0
                    for chunk in r.raw.stream(amt=chunk_size):
                        i += 1
                        while bool(is_pause.value):
                            time.sleep(1)
                        if chunk:
                            f.seek(pos)
                            f.write(chunk)
                            lock.acquire()
                            bytes_downloaded.value += len(chunk)
                            lock.release()
                            pos += len(chunk)

    def download_manager(self):
        super().download_manager()
        self._queue = Queue()
        lock = Lock()
        for i in itertools.chain(self._range_iterator, [('STOP', '')] * self._worker_num):
            self._queue.put((self._url, self._get_filename(),
                             self._chunk_size, i[0], i[1]))

        for p in range(self._worker_num):
            p = Process(
                target=self._download_worker,
                args=(self._queue, self._bytes_downloaded, lock, self._paused)
            )
            self.running_workers.append(p)
            p.start()

        for process in self.running_workers:
            process.join()
        self.uncompress_if_gzip()
        self._running = False
        self._status = DownloadStatus.FINISHED
