import requests


def int_or_none(n):
    try:
        return int(n)
    except TypeError:
        return None


def make_head_req(url):
    return requests.head(url)
