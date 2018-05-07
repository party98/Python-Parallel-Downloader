import sys
from argparse import ArgumentParser


def main():
    a = ArgumentParser(prog='pyDownload',
                       description='A pure python tool to download files from the internet using\
                        parallel threads.',
                       usage='pyDownload [--option value] url')
    a.add_argument('url', nargs='+')
    a.add_argument('-o', '--filename', help='output file', dest='filename')
    a.add_argument('-t', '--threads', help='number of threads to use',
                   type=int, dest='num_threads')
    a.add_argument('-c', '--chunk-size',
                   help='chunk size (in bytes)', type=int, dest='chunk_size')
    a.add_argument('--single-multithreaded', action='store_true',
                   help='use multithreading to download file.', dest='multithreaded')
    args = a.parse_args(sys.argv[1:])
    print(args)


if __name__ == '__main__':
    main()
