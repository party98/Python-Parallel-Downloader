# PyDownload

This package aims to provide the functionality to download large files from the internet using chunked and multithreaded downloads.


## Usage

```
import time
from pyDownload import Downloader

url = 'https://github.com/party98/Python-Parallel-Downloader/archive/master.zip'
downloader = Downloader(url=url, filename=filename)
if downloader.is_running:
    time.sleep(1)
print('File downloaded to %s' % downloader.file_name)
```
