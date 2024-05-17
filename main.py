try:
    import user_config as config
except ImportError:
    import config
from selenium import webdriver

# from selenium_stealth import stealth
import asyncio
from utils import (
    getChannelItems,
    updateChannelUrlsTxt,
    updateFile,
    sortUrlsBySpeedAndResolution,
    getTotalUrlsFromInfoList,
    getTotalUrlsFromSortedData,
    filterUrlsByPatterns,
    useAccessibleUrl,
    getChannelsBySubscribeUrls,
    checkUrlByPatterns,
    getFOFAUrlsFromRegionList,
    getChannelsByFOFA,
    mergeObjects,
    getChannelsInfoListByOnlineSearch,
    formatChannelName,
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
            extendResults = await getChannelsBySubscribeUrls(channelNames)
        if config.open_multicast:
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
        for cate, channelObj in channelItems.items():
            channelUrls = {}
            channelObjKeys = channelObj.keys()
            for name in channelObjKeys:
                pbar.set_description(
                    f"Processing {name}, {total_channels - pbar.n} channels remaining"
                )
                format_name = formatChannelName(name)
                info_list = []
                if config.open_subscribe:
                    for url, date, resolution in extendResults.get(format_name, []):
                        if url and checkUrlByPatterns(url):
                            info_list.append((url, None, resolution))
                if config.open_multicast:
                    for url in fofa_results.get(format_name, []):
                        if url and checkUrlByPatterns(url):
                            info_list.append((url, None, None))
                if config.open_online_search and pageUrl:
                    online_info_list = getChannelsInfoListByOnlineSearch(
                        self.driver, pageUrl, format_name
                    )
                    if online_info_list:
                        info_list.extend(online_info_list)
                try:
                    channelUrls[name] = filterUrlsByPatterns(
                        getTotalUrlsFromInfoList(info_list)
                    )
                    github_actions = os.environ.get("GITHUB_ACTIONS")
                    if (
                        config.open_sort
                        and not github_actions
                        or (pbar.n <= 200 and github_actions == "true")
                    ):
                        sorted_data = await sortUrlsBySpeedAndResolution(info_list)
                        if sorted_data:
                            channelUrls[name] = getTotalUrlsFromSortedData(sorted_data)
                            for (
                                url,
                                date,
                                resolution,
                            ), response_time in sorted_data:
                                logging.info(
                                    f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                                )
                    if len(channelUrls[name]) == 0:
                        channelUrls[name] = filterUrlsByPatterns(channelObj[name])
                except:
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
