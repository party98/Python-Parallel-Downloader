# flake8: noqa: E501
from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pyDownload',  # Required
    version='0.0.1.dev1',  # Required
    description='A simple package for multithreaded downloading',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/party98/Python-Parallel-Downloader',  # Optional
    author='Parth Verma',  # Optional
    author_email='v.parth98@gmail.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='downloading multithreaded parallel multithreading multithreaded-downloading download',  # Optional
    packages=find_packages(
        exclude=['contrib', 'docs', 'tests', '.*', 'requirements.txt']),  # Required
    install_requires=['requests>=2.0.0'],  # Optional
    extras_require={  # Optional
        'dev': ['pre-commit==1.8.2'],
        'test': [''],
    },
    entry_points={  # Optional
        # 'console_scripts': [
        #     'sample=sample:main',
        # ],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/party98/Python-Parallel-Downloader/issues',
        'Say Thanks!': 'https://saythanks.io/to/party98',
        'Source': 'https://github.com/party98/Python-Parallel-Downloader',
    },
)
