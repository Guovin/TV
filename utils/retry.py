from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.config import config

max_retries = 2
timeout = config.getint("Settings", "request_timeout", fallback=10)


def retry_func(func, retries=max_retries, name=""):
    """
    Retry the function
    """
    for i in range(retries):
        try:
            sleep(1)
            return func()
        except Exception as e:
            if name and i < retries - 1:
                print(f"Failed to connect to the {name}. Retrying {i+1}...")
            elif i == retries - 1:
                raise Exception(
                    f"Failed to connect to the {name} reached the maximum retries."
                )
    raise Exception(f"Failed to connect to the {name} reached the maximum retries.")


def locate_element_with_retry(driver, locator, timeout=timeout, retries=max_retries):
    """
    Locate the element with retry
    """
    wait = WebDriverWait(driver, timeout)
    for _ in range(retries):
        try:
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            driver.refresh()
    return None


def find_clickable_element_with_retry(
    driver, locator, timeout=timeout, retries=max_retries
):
    """
    Find the clickable element with retry
    """
    wait = WebDriverWait(driver, timeout)
    for _ in range(retries):
        try:
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            driver.refresh()
    return None
