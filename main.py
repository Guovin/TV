try:
    import user_config as config
except ImportError:
    import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import asyncio
from bs4 import BeautifulSoup
from utils import (
    getChannelItems,
    updateChannelUrlsTxt,
    updateFile,
    getUrlInfo,
    sortUrlsBySpeedAndResolution,
    getTotalUrls,
    checkUrlIPVType,
    checkByDomainBlacklist,
    checkByURLKeywordsBlacklist,
    filterUrlsByPatterns,
    useAccessibleUrl,
    getChannelsByExtendBaseUrls,
)
import logging
from logging.handlers import RotatingFileHandler
import os
from tqdm import tqdm

handler = RotatingFileHandler("result_new.log", encoding="utf-8")
logging.basicConfig(
    handlers=[handler],
    format="%(message)s",
    level=logging.INFO,
)


class UpdateSource:

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("blink-settings=imagesEnabled=false")
        options.add_argument("--log-level=3")
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

    def __init__(self):
        self.driver = self.setup_driver()

    async def visitPage(self, channelItems):
        channelNames = [
            name for _, channelObj in channelItems.items() for name in channelObj.keys()
        ]
        extendResults = await getChannelsByExtendBaseUrls(channelNames)
        total_channels = len(channelNames)
        pbar = tqdm(total=total_channels)
        pageUrl = await useAccessibleUrl()
        for cate, channelObj in channelItems.items():
            channelUrls = {}
            channelObjKeys = channelObj.keys()
            for name in channelObjKeys:
                pbar.set_description(
                    f"Processing {name}, {total_channels - pbar.n} channels remaining"
                )
                self.driver.get(pageUrl)
                search_box = self.driver.find_element(By.XPATH, '//input[@type="text"]')
                search_box.clear()
                search_box.send_keys(name)
                submit_button = self.driver.find_element(
                    By.XPATH, '//input[@type="submit"]'
                )
                submit_button.click()
                isFavorite = name in config.favorite_list
                pageNum = (
                    config.favorite_page_num if isFavorite else config.default_page_num
                )
                infoList = []
                for url in extendResults.get(name, []):
                    infoList.append((url, None, None))
                if pageUrl:
                    for page in range(1, pageNum + 1):
                        try:
                            if page > 1:
                                page_link = self.driver.find_element(
                                    By.XPATH,
                                    f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                )
                                page_link.click()
                            soup = BeautifulSoup(self.driver.page_source, "html.parser")
                            results = (
                                soup.find_all("div", class_="result") if soup else []
                            )
                            for result in results:
                                try:
                                    url, date, resolution = getUrlInfo(result)
                                    if (
                                        url
                                        and checkUrlIPVType(url)
                                        and checkByDomainBlacklist(url)
                                        and checkByURLKeywordsBlacklist(url)
                                    ):
                                        infoList.append((url, date, resolution))
                                except Exception as e:
                                    print(f"Error on result {result}: {e}")
                                    continue
                        except Exception as e:
                            print(f"Error on page {page}: {e}")
                            continue
                try:
                    github_actions = os.environ.get("GITHUB_ACTIONS")
                    if not github_actions or (
                        pbar.n <= 200 and github_actions == "true"
                    ):
                        sorted_data = await sortUrlsBySpeedAndResolution(infoList)
                        if sorted_data:
                            channelUrls[name] = getTotalUrls(sorted_data)
                            for (url, date, resolution), response_time in sorted_data:
                                logging.info(
                                    f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                                )
                        else:
                            channelUrls[name] = filterUrlsByPatterns(channelObj[name])
                    else:
                        channelUrls[name] = filterUrlsByPatterns(channelObj[name])
                except Exception as e:
                    print(f"Error on sorting: {e}")
                    continue
                finally:
                    pbar.update()
            updateChannelUrlsTxt(cate, channelUrls)
            await asyncio.sleep(1)
        pbar.close()

    def main(self):
        asyncio.run(self.visitPage(getChannelItems()))
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        user_final_file = getattr(config, "final_file", "result.txt")
        user_log_file = (
            "user_result.log" if os.path.exists("user_config.py") else "result.log"
        )
        updateFile(user_final_file, "result_new.txt")
        updateFile(user_log_file, "result_new.log")
        print(f"Update completed! Please check the {user_final_file} file!")


UpdateSource().main()
