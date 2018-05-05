# PyDownload

This package aims to provide the functionality to download large files from the internet using chunked and multithreaded downloads.

# Index
 - [Installation](#installation)
 - [Usage](#usage)
 - [Developer Guide](#developer-guide)
 - [SayThanks](#saythanks)

# Installation

```bash
pip install pydownload
```

# Usage

```python
import time
<<<<<<< HEAD
from pyDownload import Downloader

url = 'https://github.com/party98/Python-Parallel-Downloader/archive/master.zip'
downloader = Downloader(url=url, filename=filename)
if downloader.is_running:
    time.sleep(1)
print('File downloaded to %s' % downloader.file_name)
```

# Developer Guide

## Setting Up The Environment
 - ### Setup VirtualEnv (Recommended But Optional)
   ```bash
   pip install virtualenv
   virtualenv env
   source ./env/bin/activate
   ```
 - ### Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```
 -  ### Install pre-commit hooks
    The project uses various pre-commit hooks to enforce code quality and standards. Therefore, it is really necessary for all the contributors to install these and run before every commit else the contributions will be rejected.

    ##### Steps
    ```bash
    pre-commit install
    ```

## Running Tests
 - ### Install Dependencies
   ```
   pip install nose coverage
   ```
 - ### Run the Tests
   - #### With Coverage Report (Recommended)
     ```
     nosetests --cover-erase --cover-package=pyDownload --with-coverage --cover-branches
     ```
   - #### Without Coverage Report
     ```
     nosetests --cover-erase --cover-package=pyDownload  --cover-branches
     ```

# SayThanks

You can thank the team [here](https://saythanks.io/to/party98).
