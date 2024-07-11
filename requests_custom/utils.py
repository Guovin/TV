import requests
import re
from bs4 import BeautifulSoup
import random
from time import sleep

user_agents = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
]

headers = {
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "User-Agent": random.choice(user_agents),
}

session = requests.Session()


def get_source_requests(url, proxy=None, timeout=30):
    """
    Get the source by requests
    """
    proxies = {"http": proxy}
    headers["User-Agent"] = random.choice(user_agents)
    response = session.get(url, headers=headers, proxies=proxies, timeout=timeout)
    source = re.sub(
        r"<!--.*?-->",
        "",
        response.text,
        flags=re.DOTALL,
    )
    return source


def get_soup_requests(url, proxy=None, timeout=30):
    """
    Get the soup by requests
    """
    source = get_source_requests(url, proxy, timeout)
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
