import gzip
import itertools
import os
import shutil
import threading
from abc import abstractclassmethod, abstractmethod
from urllib.parse import urlparse

from .status import DownloadStatus
from .utils import create_file, int_or_none, make_head_req

try:
    from abc import ABC
except ImportError:
    ABC = object


class BaseDownloader(ABC):
    try:
        from abc import ABC
    except ImportError:
        from abc import ABCMeta
        __metaclass__ = ABCMeta

    def __init__(self, url, filename=None, workers=4, num_splits=10, chunk_size=1024 * 1024 * 1, wait_for_download=True,
                 auto_start=True):
        self.running_workers = []
        self._status = DownloadStatus.INITIALIZING
        self._running = False
        self._intermediate_files = []
        download_meta_data = make_head_req(url)
        self._url = download_meta_data.url
        download_headers = download_meta_data.headers
        self._download_size = int_or_none(
            download_headers.get("Content-Length"))
        self.is_gzip = download_headers.get("Content-Encoding") == "gzip"
        self._filename = filename
        self._worker_num = 1 if self._download_size is None else workers
        self._num_splits = 1 if self._download_size is None else num_splits
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

    @abstractclassmethod
    def is_paused(self):
        pass

    @property
    def wait_for_download(self):
        return self._wait_for_download

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
    def worker_num(self):
        return self._worker_num

    @worker_num.setter
    def worker_num(self, worker_num):
        if self._running is False:
            self._worker_num = 1 if self._download_size is None else worker_num

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
                self._worker_num = 1
                self._num_splits = 1
            self._range_iterator = self._download_spliter()
            self._range_iterator, self._range_list = itertools.tee(
                self._range_iterator)
            self._range_list = list(self._range_list)

    @property
    def download_size(self):
        return self._download_size

    @property
    def is_running(self):
        return self._running

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

    def uncompress_if_gzip(self):
        filename = self._get_filename()
        if self.is_gzip:
            with gzip.open(filename + ".temp", "rb") as f_in:
                with open(filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    os.remove(filename + ".temp")
        else:
            os.rename(filename + ".temp", filename)

    @abstractmethod
    def download_manager(self):
        self._running = True
        # Create file so that we are able to open it in r+ mode
        create_file(self._get_filename() + ".temp")
        self._status = DownloadStatus.RUNNING

    @abstractmethod
    def pause(self):
        if self._running:
            self._status = DownloadStatus.PAUSED

    @abstractmethod
    def resume(self):
        if self._running and bool(self.is_paused):
            self._status = DownloadStatus.RUNNING

    @abstractmethod
    def _download_worker(self):
        pass
