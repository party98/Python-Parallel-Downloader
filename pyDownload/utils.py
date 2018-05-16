import requests


def int_or_none(n):
    try:
        return int(n)
    except ValueError:
        return None
    except TypeError:
        return None


def make_head_req(url):
    return requests.head(url, allow_redirects=True)


def create_file(filename):
    open(filename, 'w').close()
