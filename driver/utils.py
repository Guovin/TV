from driver.setup import setup_driver
from utils.retry import retry_func
from time import sleep
import re
from bs4 import BeautifulSoup


def get_soup_driver(url):
    """
    Get the soup by driver
    """
    driver = setup_driver()
    retry_func(lambda: driver.get(url), name=url)
    sleep(1)
    source = re.sub(
        r"<!--.*?-->",
        "",
        driver.page_source,
        flags=re.DOTALL,
    )
    soup = BeautifulSoup(source, "html.parser")
    driver.close()
    driver.quit()
    return soup
