# -*- coding: utf-8 -*-

from .process_downloader import ProcessDownloader
from .thread_downloader import ThreadDownloader


class DownloaderFactory(object):
    def __new__(cls, multithreaded=False, *args, **kwargs):
        if multithreaded:
            return ThreadDownloader(*args, **kwargs)
        else:
            return ProcessDownloader(*args, **kwargs)
