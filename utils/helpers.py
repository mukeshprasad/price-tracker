import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils.constants import URL_PATTERN, HEADERS
import random


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


def generate_new_user_agent():
    version_components = [str(random.randint(0, 9999)) for _ in range(4)]
    version_number = ".".join(version_components)
    new_user_agent = f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version_number} Safari/537.36"
    return new_user_agent


def get_soup(url):
    headers = HEADERS
    for _ in range(100):
        headers["User-Agent"] = generate_new_user_agent()
        webpage = requests.get(url, headers=headers)
        if "api-services" not in str(webpage.content):
            print(headers)
            soup = BeautifulSoup(webpage.content, "lxml")
            price = soup.find("span", class_="a-price-whole").get_text()
            if price:
                break

    return soup
