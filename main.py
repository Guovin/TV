try:
    import user_config as config
except ImportError:
    import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from selenium_stealth import stealth
import asyncio
from bs4 import BeautifulSoup
from utils import (
    getChannelItems,
    updateChannelUrlsTxt,
    updateFile,
    getResultsFromSoup,
    sortUrlsBySpeedAndResolution,
    getTotalUrls,
    filterUrlsByPatterns,
    useAccessibleUrl,
    getChannelsByExtendBaseUrls,
    checkUrlByPatterns,
    getFOFAUrlsFromRegionList,
    getChannelsByFOFA,
    mergeObjects,
    getTotalUrlsFromInfoList,
)
import logging
from logging.handlers import RotatingFileHandler
import os
from tqdm import tqdm
import re
import time

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
        # stealth(
        #     driver,
        #     languages=["en-US", "en"],
        #     vendor="Google Inc.",
        #     platform="Win32",
        #     webgl_vendor="Intel Inc.",
        #     renderer="Intel Iris OpenGL Engine",
        #     fix_hairline=True,
        # )
        return driver

    def __init__(self):
        self.driver = self.setup_driver()

    async def visitPage(self, channelItems):
        channelNames = [
            name for _, channelObj in channelItems.items() for name in channelObj.keys()
        ]
        if config.open_subscribe:
            extendResults = await getChannelsByExtendBaseUrls(channelNames)
        if config.open_multicast:
            print(f"Getting channels by FOFA...")
            fofa_urls = getFOFAUrlsFromRegionList()
            fofa_results = {}
            for url in fofa_urls:
                if url:
                    self.driver.get(url)
                    time.sleep(10)
                    fofa_source = re.sub(
                        r"<!--.*?-->", "", self.driver.page_source, flags=re.DOTALL
                    )
                    fofa_channels = getChannelsByFOFA(fofa_source)
                    fofa_results = mergeObjects(fofa_results, fofa_channels)
        total_channels = len(channelNames)
        pbar = tqdm(total=total_channels)
        pageUrl = await useAccessibleUrl() if config.open_online_search else None
        wait = WebDriverWait(self.driver, 10)
        for cate, channelObj in channelItems.items():
            channelUrls = {}
            channelObjKeys = channelObj.keys()
            for name in channelObjKeys:
                pbar.set_description(
                    f"Processing {name}, {total_channels - pbar.n} channels remaining"
                )
                info_list = []
                if config.open_subscribe:
                    for url, date, resolution in extendResults.get(name, []):
                        if url and checkUrlByPatterns(url):
                            info_list.append((url, None, resolution))
                if config.open_multicast:
                    for url in fofa_results.get(name, []):
                        if url and checkUrlByPatterns(url):
                            info_list.append((url, None, None))
                if config.open_online_search and pageUrl:
                    self.driver.get(pageUrl)
                    search_box = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//input[@type="text"]')
                        )
                    )
                    search_box.clear()
                    search_box.send_keys(name)
                    submit_button = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//input[@type="submit"]')
                        )
                    )
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    isFavorite = name in config.favorite_list
                    pageNum = (
                        config.favorite_page_num
                        if isFavorite
                        else config.default_page_num
                    )
                    for page in range(1, pageNum + 1):
                        try:
                            if page > 1:
                                page_link = wait.until(
                                    EC.element_to_be_clickable(
                                        (
                                            By.XPATH,
                                            f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                        )
                                    )
                                )
                                self.driver.execute_script(
                                    "arguments[0].click();", page_link
                                )
                            source = re.sub(
                                r"<!--.*?-->",
                                "",
                                self.driver.page_source,
                                flags=re.DOTALL,
                            )
                            soup = BeautifulSoup(source, "html.parser")
                            if soup:
                                results = getResultsFromSoup(soup, name)
                                for result in results:
                                    url, date, resolution = result
                                    if url and checkUrlByPatterns(url):
                                        info_list.append((url, date, resolution))
                        except Exception as e:
                            print(f"Error on page {page}: {e}")
                            continue
                try:
                    github_actions = os.environ.get("GITHUB_ACTIONS")
                    if not github_actions or (
                        pbar.n <= 200 and github_actions == "true"
                    ):
                        if config.open_sort:
                            sorted_data = await sortUrlsBySpeedAndResolution(info_list)
                            if sorted_data:
                                channelUrls[name] = getTotalUrls(sorted_data)
                                for (
                                    url,
                                    date,
                                    resolution,
                                ), response_time in sorted_data:
                                    logging.info(
                                        f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                                    )
                            else:
                                channelUrls[name] = filterUrlsByPatterns(
                                    channelObj[name]
                                )
                        else:
                            channelUrls[name] = filterUrlsByPatterns(
                                getTotalUrlsFromInfoList(info_list)
                            )
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
