# PyDownload [![PyPI version](https://badge.fury.io/py/pyDownload.svg)](https://badge.fury.io/py/pyDownload) [![Build Status](https://travis-ci.org/party98/pyDownload.svg?branch=master)](https://travis-ci.org/party98/pyDownload) [![codecov](https://codecov.io/gh/party98/pyDownload/branch/master/graph/badge.svg)](https://codecov.io/gh/party98/pyDownload)

This package aims to provide the functionality to download large files from the internet using chunked and multithreaded/multiprocessed downloads.

# Index
 - [Command Line Usage](#command-line-usage)
 - [Features](#features)
 - [Installation](#installation)
 - [Usage](#usage)
 - [Developer Guide](#developer-guide)
 - [Bug Reporting Guide](#bug-reporting-guide)
 - [Contribution Guide](#contribution-guide)
 - [SayThanks](#saythanks)

# Command Line usage

The package can be used to perform fast downloads via the CLI.

### Usage

```bash
pyDownload https://github.com/party98/Python-Parallel-Downloader/archive/master.zip
```

### Config Options
```bash
positional arguments:
  url                   list of urls to download

optional arguments:
  -h, --help            show this help message and exit
  -m, --multithreading  switch between multithreading and multiprocessing
  -o FILENAME, --output FILENAME
                        output file
  -t NUM_THREADS, --threads NUM_THREADS
                        number of threads to use
  -c CHUNK_SIZE, --chunk-size CHUNK_SIZE
                        chunk size (in bytes)
  --version             display the version of pyDownload being used
```

# Features

 - Written in pure python.
 - Supports ability to perform multithreaded downloads from any url if the server supports.
 - Small and concise API therefore easy to integrate in python code.

# Installation

```bash
pip install pydownload
```

# Usage

```python
import time
from pyDownload import Downloader

url = 'https://github.com/party98/Python-Parallel-Downloader/archive/master.zip'
downloader = Downloader(url=url)
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
   pip install .[dev]
   ```
 -  ### Install pre-commit hooks
    The project uses various pre-commit hooks to enforce code quality and standards. Therefore, it is really necessary for all the contributors to install these and run before every commit else the contributions will be rejected.

    ##### Steps
    ```bash
    pre-commit install
    ```

## Running Tests
 - ### Install Dependencies
   ```bash
   pip install .[test]
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

# Bug Reporting Guide

You can report bugs [here](https://github.com/party98/pyDownload/issues).

 - Make sure you are using the latest version. (Check by running `pyDownload --version`).
 - Search for the issue in existing issues (open & closed) and create only if the issue is not mentioned.
 - Fill the issue template correctly.

Note: If you feel that you can fix the issue, you are more than welcome to submit a PR.

# Contribution Guide

Contributors are welcome to make this package more awesome. But before you do, make sure that you have read the following limited but important guidelines.

 - Make sure that the issue that you are trying to fix exists [here](https://github.com/party98/pyDownload/issues). Create one if it does not.
 - Make sure that you perform `flake8` checks on the code before you submit a PR.
 - Write unittests and comments for the changes that you have made.
 - Make sure your branch is updated with the `development` branch.
 - All PRs should be submitted to `development` branch. PRs to any other branch will be rejected.
 - Please install and perform `pre-commit` check on all your commits to maintain code quality


# SayThanks

You can thank the team [here](https://saythanks.io/to/party98).
