from argparse import ArgumentParser

import progressbar

from . import Downloader


def initializee_progress_bar(max_value):
    if max_value is None:
        max_value = progressbar.UnknownLength
    widgets = [progressbar.Percentage(), ' (', progressbar.DataSize(), ' of',
               progressbar.DataSize(
                   'max_value'), ' )', progressbar.AdaptiveTransferSpeed(),
               progressbar.Bar(marker='█'), progressbar.Timer(), ' ', progressbar.AdaptiveETA()]
    return progressbar.DataTransferBar(max_value=max_value, widgets=widgets)


def initiate_download(args):
    download = Downloader(url=args.url[0], chunk_size=args.chunk_size, threads=args.num_threads,
                          multithreaded=not args.multithreaded, filename=args.filename,
                          auto_start=False, wait_for_download=False)
    bar = initializee_progress_bar(download.download_size)
    download.start_download(wait_for_download=False)
    while download.is_running:
        bar.update(download.bytes_downloaded)
    bar.finish('\nFile saved at %s\n' % download.file_name)


def main():
    a = ArgumentParser(prog='pyDownload',
                       description='A pure python tool to download files from the internet using\
                        parallel threads.',
                       usage='pyDownload [--option value] url')
    a.add_argument('url', nargs='+')
    a.add_argument('-o', '--filename', help='output file', dest='filename')
    a.add_argument('-t', '--threads', help='number of threads to use',
                   type=int, dest='num_threads', default=4)
    a.add_argument('-c', '--chunk-size',
                   help='chunk size (in bytes)', type=int, dest='chunk_size', default=1024)
    a.add_argument('--single-multithreaded', action='store_true',
                   help='use multithreading to download file.', dest='multithreaded')
    a.add_argument('--version', action='store_true',
                   help='display the version of pyDownload being used', dest='version')
    args = a.parse_args()
    initiate_download(args)


if __name__ == '__main__':
    main()
