from random import choice
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

try:
    import requests

    HAS_REQUEST = True
except ImportError:
    HAS_REQUEST = False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "TE": "trailers",
}

PROXIES = {
    "http://o16rgq:2Abv0p@196.17.79.31:8000": 0,
    "http://o16rgq:2Abv0p@45.4.199.119:8000": 0,
    "http://N6D7aC:r75Rebp@38.152.204.28:8000": 0,
    "http://N6D7aC:r75Rebp@38.152.69.244:8000": 0,
    "http://N6D7aC:r75Rebp@38.152.25.66:8000": 0,
}

DEFAULT_TIMEOUT = 60

basestring = (str, bytes)

allowed_args = (
    "auth",
    "data",
    "headers",
    "verify",
    "cert",
    "config",
    "hooks",
    "proxies",
    "cookies",
)


def _query(url, method, kwargs):
    data = None
    if "data" in kwargs:
        data = kwargs.pop("data")
    if type(data) in (dict, list, tuple):
        data = urlencode(data)

    if isinstance(method, basestring) and method.lower() == "get" and data:
        if "?" not in url:
            url += "?"
        elif url[-1] not in ("?", "&"):
            url += "&"
        url += data
        data = None

    if data:
        data = data.encode("utf-8")
    return url, data


def _proxy():
    proxy = choice(list(PROXIES.keys()))
    value = min(PROXIES.values())
    mused = list(PROXIES.keys())[list(PROXIES.values()).index(value)]
    if value > 1 and proxy != PROXIES[mused]:
        proxy = mused

    count = PROXIES.get(proxy) + 1
    PROXIES[proxy] = count
    return proxy


def _requests(url, kwargs):
    encoding = kwargs.get("encoding")
    method = kwargs.get("method", "get").lower()
    session = kwargs.get("session")
    if session:
        meth = getattr(session, str(method))
    else:
        meth = getattr(requests, str(method))
    if method == "get":
        url, data = _query(url, method, kwargs)
    kw = {}
    for k in allowed_args:
        if k in kwargs:
            kw[k] = kwargs[k]
    proxies = _proxy()
    resp = meth(
        url=url,
        headers=HEADERS,
        timeout=kwargs.get("timeout", DEFAULT_TIMEOUT),
        proxies={"http": proxies},
        **kw,
    )
    if not (200 <= resp.status_code < 300):
        raise HTTPError(
            resp.url,
            resp.status_code,
            resp.reason,
            resp.headers,
            None,
        )
    if encoding:
        resp.encoding = encoding
    html = resp.text
    return html


def _urllib(url, kwargs):
    method = kwargs.get("method")
    url, data = _query(
        url,
        method,
        kwargs,
    )
    return urlopen(
        url,
        data,
        timeout=kwargs.get("timeout", DEFAULT_TIMEOUT),
    )


def url_opener(url, kwargs):
    if HAS_REQUEST:
        return _requests(url, kwargs)
    return _urllib(url, kwargs)
