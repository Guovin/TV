from selenium import webdriver
from selenium_stealth import stealth


def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    # options.add_argument("--headless")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)
    # options.add_argument("blink-settings=imagesEnabled=false")
    # options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


if __name__ == '__main__':
    setup_driver()
