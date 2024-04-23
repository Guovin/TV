from trans.trans2m3u import trans2m3u

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
    compareSpeedAndResolution,
    getTotalUrls,
    checkUrlIPVType,
    checkByDomainBlacklist,
    checkByURLKeywordsBlacklist,
    filterUrlsByPatterns,
    checkUrlAccessible,
)
import logging
from logging.handlers import RotatingFileHandler
import os
from tqdm import tqdm

console_handler = logging.StreamHandler()

handler = RotatingFileHandler("result_new.log", encoding="utf-8")
logging.basicConfig(
    handlers=[handler, console_handler],
    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
    datefmt="%d-%M-%Y %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger("tv")


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
        total_channels = sum(len(channelObj) for _, channelObj in channelItems.items())
        pbar = tqdm(total=total_channels)
        for cate, channelObj in channelItems.items():
            channelUrls = {}
            channelObjKeys = channelObj.keys()
            for name in channelObjKeys:
                logger.info(f"--------------------------- name: {name}")
                pbar.set_description(
                    f"Processing {name}, {total_channels - pbar.n} channels remaining"
                )
                isFavorite = name in config.favorite_list
                pageNum = (
                    config.favorite_page_num if isFavorite else config.default_page_num
                )
                baseUrl = "https://www.foodieguide.com/iptvsearch/"
                infoList = []
                urlAccessible = await checkUrlAccessible(baseUrl)
                if urlAccessible:
                    for page in range(1, pageNum + 1):
                        try:
                            page_url = f"{baseUrl}?page={page}&s={name}"
                            logger.info("========== page_url: {}".format(page_url))
                            self.driver.get(page_url)
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "div.tables")
                                )
                            )
                            soup = BeautifulSoup(self.driver.page_source, "html.parser")
                            tables_div = soup.find("div", class_="tables")
                            results = (
                                tables_div.find_all("div", class_="result")
                                if tables_div
                                else []
                            )
                            for result in results:
                                try:
                                    url, date, resolution = getUrlInfo(result)
                                    logger.info(f"-------> name：{name} url: {url}")
                                    if (
                                        url
                                        and checkUrlIPVType(url)
                                        and checkByDomainBlacklist(url)
                                        and checkByURLKeywordsBlacklist(url)
                                    ):
                                        infoList.append((url, date, resolution))
                                except Exception as e:
                                    logger.info(f"Error on result {result}: {e}")
                                    continue
                        except Exception as e:
                            logger.info(f"Error on page {page}: {e}")
                            continue
                try:
                    if infoList:
                        from datetime import datetime
                        current_date = datetime.now().strftime('%m-%d-%Y')
                        for url in channelObj[name]:
                            infoList.append((url,current_date,'1920x1080'))
                        sorted_data = await compareSpeedAndResolution(infoList)
                        if sorted_data:
                            for (url, date, resolution), response_time in sorted_data:
                                logger.info(
                                    f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                                )
                            channelUrls[name] = (
                                    getTotalUrls(sorted_data) or channelObj[name]
                            )
                            for url in channelUrls[name]:
                                logger.info(f"----------> name：{name} url: {url}")
                    else:
                        channelUrls[name] = filterUrlsByPatterns(channelObj[name])
                except Exception as e:
                    logger.info(f"Error on sorting: {e}")
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
        logger.info(f"user_final_file: {user_final_file}")
        user_log_file = (
            "user_result.log" if os.path.exists("user_config.py") else "result.log"
        )
        logger.info(f"user_log_file: {user_log_file}")
        updateFile(user_final_file, "result_new.txt")
        updateFile(user_log_file, "result_new.log")
        logger.info(f"Update completed! Please check the {user_final_file} file!")
        trans2m3u(user_final_file, "playlist.m3u")


UpdateSource().main()
