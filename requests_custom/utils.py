import requests
import re
from bs4 import BeautifulSoup
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
]

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": random.choice(user_agents),
}

session = requests.Session()


def get_source_requests(url, proxy=None):
    """
    Get the source by requests
    """
    proxies = {"http": proxy}
    response = session.get(url, headers=headers, proxies=proxies, timeout=30)
    source = re.sub(
        r"<!--.*?-->",
        "",
        response.text,
        flags=re.DOTALL,
    )
    return source


def get_soup_requests(url, proxy=None):
    """
    Get the soup by requests
    """
    source = get_source_requests(url, proxy)
    soup = BeautifulSoup(source, "html.parser")
    return soup


def close_session():
    """
    Close the requests session
    """
    session.close()


def reset_user_agent():
    """
    Reset the user agent
    """
    global headers
    headers["User-Agent"] = random.choice(user_agents)
