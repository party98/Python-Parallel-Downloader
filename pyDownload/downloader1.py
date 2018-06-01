import gzip
import itertools
import os
import shutil
import threading
# import time
from itertools import chain
from multiprocessing import Lock, Process, Queue, Value
from urllib.parse import urlparse

import requests

from .status import DownloadStatus
from .utils import create_file, int_or_none, make_head_req


class Downloader(object):
    def __init__(
        self,
        url,
        filename=None,
        threads=10,
        chunk_size=1024,
        auto_start=True,
        multithreaded=True,
        wait_for_download=True,
        num_splits=10
    ):
        self._status = DownloadStatus.INITIALIZING
        self._paused = False
        self._running = False
        self._is_multithreaded = multithreaded
        self._intermediate_files = []
        self._bytes_downloaded = Value('i', 0)
        self._num_splits = num_splits
        download_meta_data = make_head_req(url)
        self._url = download_meta_data.url
        download_headers = download_meta_data.headers
        self._download_size = int_or_none(
            download_headers.get("Content-Length"))
        self.is_gzip = download_headers.get("Content-Encoding") == "gzip"
        if self._download_size is None:
            self._is_multithreaded = False
        self._filename = filename
        self._thread_num = 1 if self._download_size is None else threads
        self._range_iterator = self._download_spliter()
        self._range_iterator, self._range_list = itertools.tee(
            self._range_iterator)
        self._range_list = list(self._range_list)
        self._chunk_size = chunk_size
        self._manager = threading.Thread(target=self.download_manager)
        self._wait_for_download = wait_for_download
        self._status = DownloadStatus.READY
        if auto_start:
            self._manager.start()
            self._status = DownloadStatus.STARTED
            if self._wait_for_download:
                self._manager.join()

    @property
    def status(self):
        return self._status

    @property
    def wait_for_download(self):
        return self._wait_for_download

    # @property
    # def multithreaded(self):
    #     return self._is_multithreaded
    #
    # @multithreaded.setter
    # def multithreaded(self, value):
    #     if self._running is False:
    #         self._is_multithreaded = value
    #         if self._is_multithreaded:
    #             self._range_iterator = self._download_spliter()
    #             self._range_iterator, self._range_list = itertools.tee(
    #                 self._range_iterator)
    #             self._range_list = list(self._range_list)

    @property
    def file_name(self):
        return self._get_filename()

    @file_name.setter
    def file_name(self, filename):
        if self._running is False:
            self._filename = filename

    @property
    def num_splits(self):
        return self._num_splits

    @num_splits.setter
    def num_splits(self, num_splits):
        if self._running is False:
            self._num_splits = 1 if self._download_size is None else num_splits
            self._range_iterator = self._download_spliter()
            self._range_iterator, self._range_list = itertools.tee(
                self._range_iterator)
            self._range_list = list(self._range_list)

    @property
    def thread_num(self):
        return self._thread_num

    @thread_num.setter
    def thread_num(self, thread_num):
        if self._running is False:
            self._thread_num = 1 if self._download_size is None else thread_num

    @property
    def chunk_size(self):
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, chunk):
        if self._running is False:
            self._chunk_size = chunk

    @property
    def download_url(self):
        return self._url

    @download_url.setter
    def download_url(self, url):
        if self._running is False:
            download_meta_data = make_head_req(url)
            self._url = download_meta_data.url
            download_headers = download_meta_data.headers
            self._download_size = int_or_none(
                download_headers.get("Content-Length"))
            self.is_gzip = download_headers.get("Content-Encoding") == "gzip"
            if self._download_size is None:
                self._thread_num = 1
                self._num_splits = 1
            self._range_iterator = self._download_spliter()
            self._range_iterator, self._range_list = itertools.tee(
                self._range_iterator)
            self._range_list = list(self._range_list)

    @property
    def bytes_downloaded(self):
        return self._bytes_downloaded.value

    @property
    def download_size(self):
        return self._download_size

    @property
    def is_running(self):
        return self._running

    def pause(self):
        if self._running:
            self._paused = True
            DownloadStatus.PAUSED

    def resume(self):
        if self._running and self._paused:
            print('Resuming')
            self._paused = False
            DownloadStatus.RUNNING

    def start_download(self, wait_for_download=True):
        self._wait_for_download = wait_for_download
        if self._running is False:
            self._manager.start()
            self._status = DownloadStatus.STARTED
            if self._wait_for_download:
                self._manager.join()

    def _get_filename(self):
        if self._filename is None:
            return [i for i in urlparse(
                self._url).path.split("/") if i != ""][-1]
        return self._filename

    def _download_spliter(self):
        last = 0
        if self._download_size is None:
            yield (None, None)
        else:
            if self._download_size < self._num_splits:
                self._num_splits = self._download_size
            for i in range(self._num_splits):
                num_splits = (self._download_size -
                              last) // (self._num_splits - i)
                yield (last, int(last + num_splits) - 1)
                last = last + num_splits

    @staticmethod
    def _download_thread(queue, bytes_downloaded, lock):
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
                        # while self._paused:
                        #     time.sleep(1)
                        if chunk:
                            f.seek(pos)
                            f.write(chunk)
                            lock.acquire()
                            bytes_downloaded.value += len(chunk)
                            lock.release()
                            pos += len(chunk)

    def uncompress_if_gzip(self):
        filename = self._get_filename()
        if self.is_gzip:
            with gzip.open(filename + ".temp", "rb") as f_in:
                with open(filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    os.remove(filename + ".temp")
        else:
            os.rename(filename + ".temp", filename)

    def download_manager(self):
        self._running = True
        self.running_processes = []
        # Create file so that we are able to open it in r+ mode
        create_file(self._get_filename()+".temp")
        self._status = DownloadStatus.RUNNING
        # if self._is_multithreaded is True:
        self._queue = Queue()
        lock = Lock()
        for i in chain(self._range_iterator, [('STOP', '')]*self._thread_num):
            self._queue.put((self._url, self._get_filename(),
                             self._chunk_size, i[0], i[1]))

        for p in range(self._thread_num):
            p = Process(
                target=self._download_thread,
                args=(self._queue, self._bytes_downloaded, lock)
            )
            self.running_processes.append(p)
            p.start()

        for process in self.running_processes:
            process.join()
        # else:
        #     self._download_thread()
        self.uncompress_if_gzip()
        self._running = False
        self._status = DownloadStatus.FINISHED

# if __name__ == "__main__":
#     filename = "a.txt"
#     threads = 10
#     url = "https://raw.githubusercontent.com/ambv/black/master/.flake8"
#     d = Downloader(url, filename="ads")
