import gzip
import itertools
import os
import shutil
import threading

import requests

from .utils import create_file, int_or_none, make_head_req

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class Downloader(object):
    def __init__(
        self,
        url,
        filename=None,
        threads=10,
        chunk_size=1024,
        auto_start=True,
        multithreaded=True,
        wait_for_download=True
    ):

        self._running = False
        self._is_multithreaded = multithreaded
        self._intermediate_files = []
        self._bytes_downloaded = 0
        download_meta_data = make_head_req(url)
        self._url = download_meta_data.url
        download_headers = download_meta_data.headers
        self._download_size = int_or_none(
            download_headers.get("Content-Length"))
        self.is_gzip = download_headers.get("Content-Encoding") == "gzip"
        if self._download_size is None:
            self._is_multithreaded = False
        self._filename = filename
        self._thread_num = threads
        if self._is_multithreaded:
            self._range_iterator = self._download_spliter()
            self._range_iterator, self._range_list = itertools.tee(
                self._range_iterator)
            self._range_list = list(self._range_list)
        self._chunk_size = chunk_size
        self._manager = threading.Thread(target=self.download_manager)
        self._wait_for_download = wait_for_download
        if auto_start:
            self._manager.start()
            if self._wait_for_download:
                self._manager.join()

    @property
    def wait_for_download(self):
        return self._wait_for_download

    @property
    def multithreaded(self):
        return self._is_multithreaded

    @multithreaded.setter
    def multithreaded(self, value):
        if self._running is False:
            self._is_multithreaded = value
            if self._is_multithreaded:
                self._range_iterator = self._download_spliter()
                self._range_iterator, self._range_list = itertools.tee(
                    self._range_iterator)
                self._range_list = list(self._range_list)

    @property
    def file_name(self):
        return self._get_filename()

    @file_name.setter
    def file_name(self, filename):
        if self._running is False:
            self._filename = filename

    @property
    def thread_num(self):
        return self._thread_num

    @thread_num.setter
    def thread_num(self, thread_count):
        if self._running is False:
            self._thread_num = thread_count
            self._range_iterator = self._download_spliter()
            self._range_iterator, self._range_list = itertools.tee(
                self._range_iterator)
            self._range_list = list(self._range_list)

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
                self._is_multithreaded = False
            else:
                self._is_multithreaded = True
            if self._is_multithreaded:
                self._range_iterator = self._download_spliter()
                self._range_iterator, self._range_list = itertools.tee(
                    self._range_iterator)
                self._range_list = list(self._range_list)

    @property
    def bytes_downloaded(self):
        return self._bytes_downloaded

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
            if self._wait_for_download:
                self._manager.join()

    def _get_filename(self):
        if self._filename is None:
            return [i for i in urlparse(
                self._url).path.split("/") if i != ""][-1]
        return self._filename

    def _download_spliter(self):
        last = 0
        if self._download_size < self._thread_num:
            self._thread_num = self._download_size
        for i in range(self._thread_num):
            split_size = (self._download_size - last) // (self._thread_num - i)
            yield (last, int(last + split_size) - 1)
            last = last + split_size

    def _download_thread(self, thread_id, range_start=0, range_end=None):
        filename = self._get_filename()
        if range_start is not None and range_end is not None:
            header = {"Range": "bytes=%s-%s" % (range_start, range_end)}
        else:
            header = {}
        with requests.get(url=self._url, stream=True, headers=header) as r:
            with open("%s.temp" % filename, "rb+") as f:
                pos = range_start
                i = 0
                for chunk in r.raw.stream(amt=self._chunk_size):
                    i += 1
                    if chunk:
                        f.seek(pos)
                        f.write(chunk)
                        self._bytes_downloaded += len(chunk)
                        pos += len(chunk)
        self._intermediate_files.append("%s-%s.part" % (filename, thread_id))

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
        self.running_threads = []
        # Create file so that we are able to open it in r+ mode
        create_file(self._get_filename()+".temp")
        if self._is_multithreaded is True:
            for thread_num, down_range in zip(range(10), self._range_iterator):
                t = threading.Thread(
                    target=self._download_thread, args=(
                        thread_num, down_range[0], down_range[1])
                )
                self.running_threads.append(t)
                t.start()

            for thread in self.running_threads:
                thread.join()
        else:
            self._download_thread(thread_id=0)
        self.uncompress_if_gzip()
        self._running = False


# if __name__ == "__main__":
#     filename = "a.txt"
#     threads = 10
#     url = "https://raw.githubusercontent.com/ambv/black/master/.flake8"
#     d = Downloader(url, filename="ads")
