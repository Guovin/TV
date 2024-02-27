import selenium
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import os
import re
import requests
from selenium_stealth import stealth
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import asyncio
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime


class GetSource:
    source_file = "demo.txt"
    finalFile = "result.txt"
    importantList = [
        "珠江",
        "开平综合",
        "开平生活",
        "CCTV1",
        "CCTV5",
        "CCTV5+",
        "CCTV13",
        "广东体育",
        "广东卫视",
        "大湾区卫视",
        "浙江卫视",
        "湖南卫视",
        "翡翠台",
    ]
    importantUrlsNum = 20
    filter_invalid_url = True

    def __init__(self):
        self.driver = self.setup_driver()
        self.main()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("blink-settings=imagesEnabled=false")
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

    def getChannelItems(self):
        # Open the source file and read all lines.
        with open(self.source_file, "r") as f:
            lines = f.readlines()

        # Create a dictionary to store the channels.
        channels = {}
        current_channel = ""
        pattern = r"^(.*?),(?!#genre#)(.*?)$"

        for line in lines:
            line = line.strip()
            if "#genre#" in line:
                # This is a new channel, create a new key in the dictionary.
                current_channel = line.split(",")[0]
                channels[current_channel] = {}
            else:
                # This is a url, add it to the list of urls for the current channel.
                match = re.search(pattern, line)
                if match:
                    if match.group(1) not in channels[current_channel]:
                        channels[current_channel][match.group(1)] = [match.group(2)]
                    else:
                        channels[current_channel][match.group(1)].append(match.group(2))
        return channels

    async def getSpeed(self, url):
        async with aiohttp.ClientSession() as session:
            start = time.time()
            try:
                async with session.get(url, timeout=5) as response:
                    resStatus = response.status
            except:
                return url, float("inf")
            end = time.time()
            if resStatus == 200:
                return url, end - start
            else:
                return url, float("inf")

    async def compareSpeed(self, infoList):
        response_times = await asyncio.gather(
            *(self.getSpeed(url) for url, _, _ in infoList)
        )
        # Filter out invalid links if filter_invalid_url is True
        if self.filter_invalid_url:
            valid_responses = [
                (info, rt)
                for info, rt in zip(infoList, response_times)
                if rt[1] != float("inf")
            ]
        else:
            valid_responses = list(zip(infoList, response_times))
        sorted_res = sorted(valid_responses, key=lambda x: x[1][1])
        infoList_new = [
            (url, date, resolution) for (url, date, resolution), _ in sorted_res
        ]
        return infoList_new

    def removeFile(self):
        if os.path.exists(self.finalFile):
            os.remove(self.finalFile)

    def outputTxt(self, cate, channelUrls):
        # Update the final file.
        with open(self.finalFile, "a") as f:
            f.write(cate + ",#genre#\n")
            for name, urls in channelUrls.items():
                for url in urls:
                    if url is not None:
                        f.write(name + "," + url + "\n")
            f.write("\n")

    async def visitPage(self, channelItems):
        self.driver.get("https://www.foodieguide.com/iptvsearch/")
        self.removeFile()
        for cate, channelObj in channelItems.items():
            channelUrls = {}
            for name in channelObj.keys():
                try:
                    element = self.driver.find_element(By.ID, "search")
                    element.clear()
                    element.send_keys(name)
                    self.driver.find_element(By.ID, "form1").find_element(
                        By.NAME, "Submit"
                    ).click()
                except NoSuchElementException:
                    print(f"Element not found when searching for {name}")
                    continue
                infoList = []
                isImportant = name in self.importantList
                useNum = self.importantUrlsNum if isImportant else 10
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                tables_div = soup.find("div", class_="tables")
                results = (
                    tables_div.find_all("div", class_="result") if tables_div else []
                )
                for result in results[:useNum]:
                    m3u8_div = result.find("div", class_="m3u8")
                    url = m3u8_div.text.strip() if m3u8_div else None
                    info_div = m3u8_div.find_next_sibling("div") if m3u8_div else None
                    date = resolution = None
                    if info_div:
                        info_text = info_div.text.strip()
                        date, resolution = (
                            (
                                info_text.partition(" ")[0]
                                if info_text.partition(" ")[0]
                                else None
                            ),
                            (
                                info_text.partition(" ")[2].partition("•")[2]
                                if info_text.partition(" ")[2].partition("•")[2]
                                else None
                            ),
                        )
                    infoList.append((url, date, resolution))
                infoList.sort(
                    key=lambda x: (
                        x[1] is not None,
                        datetime.strptime(x[1], "%m-%d-%Y") if x[1] else None,
                    ),
                    reverse=True,
                )  # Sort by date
                infoList = await self.compareSpeed(infoList)  # Sort by speed
                infoList.sort(
                    key=lambda x: (
                        x[2] is not None,
                        (
                            int(x[2].split("x")[0]) * int(x[2].split("x")[1])
                            if x[2]
                            else 0
                        ),
                    ),
                    reverse=True,
                )  # Sort by resolution
                urls = list(dict.fromkeys(url for url, _, _ in infoList))
                channelUrls[name] = urls
            self.outputTxt(cate, channelUrls)
            await asyncio.sleep(1)

    def main(self):
        asyncio.run(self.visitPage(self.getChannelItems()))


GetSource()
