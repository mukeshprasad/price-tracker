import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from constants import URL_PATTERN, HEADERS


def get_url_from_message(message):
    url = None
    match = re.search(URL_PATTERN, message)
    if match:
        url = match.group()
        return True, url
    return False, url


def get_platform(url):
    domain = urlparse(url).netloc
    platform = domain.split(".")[-2]
    return platform


def get_soup(url):
    webpage = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")
    return soup
