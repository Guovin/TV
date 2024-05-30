try:
    import user_config as config
except ImportError:
    import config
from selenium import webdriver
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
    getChannelsByFOFA,
    getChannelsInfoListByOnlineSearch,
    formatChannelName,
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
        return driver

    def __init__(self):
        self.driver = self.setup_driver()
        self.tasks = []
        self.results = {}
        self.channel_queue = asyncio.Queue()
        self.pbar = None
        self.total = 0

    async def process_channel(self):
        while not self.channel_queue.empty():
            cate, name, old_urls = await self.channel_queue.get()
            channel_urls = []
            format_name = formatChannelName(name)
            info_list = []
            if config.open_subscribe:
                for url, date, resolution in self.results["open_subscribe"].get(
                    format_name, []
                ):
                    if url and checkUrlByPatterns(url):
                        info_list.append((url, None, resolution))
            if config.open_multicast:
                for url in self.results["open_multicast"].get(format_name, []):
                    if url and checkUrlByPatterns(url):
                        info_list.append((url, None, None))
            if config.open_online_search and self.results["open_online_search"]:
                online_info_list = getChannelsInfoListByOnlineSearch(
                    self.driver, self.results["open_online_search"], format_name
                )
                if online_info_list:
                    info_list.extend(online_info_list)
            try:
                channel_urls = filterUrlsByPatterns(getTotalUrlsFromInfoList(info_list))
                github_actions = os.environ.get("GITHUB_ACTIONS")
                if (
                    config.open_sort
                    and not github_actions
                    or (self.pbar.n <= 200 and github_actions == "true")
                ):
                    sorted_data = await sortUrlsBySpeedAndResolution(info_list)
                    if sorted_data:
                        channel_urls = getTotalUrlsFromSortedData(sorted_data)
                        for (
                            url,
                            date,
                            resolution,
                        ), response_time in sorted_data:
                            logging.info(
                                f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                            )
                if len(channel_urls) == 0:
                    channel_urls = filterUrlsByPatterns(old_urls)
            except:
                pass
            await updateChannelUrlsTxt(cate, name, channel_urls)
            self.channel_queue.task_done()

    async def run_task(self, task, pbar):
        result = await task
        pbar.update()
        self.update_progress(f"正在更新...", int((self.pbar.n / self.total) * 100))
        return result

    async def visitPage(self, channel_items):
        task_dict = {
            "open_subscribe": getChannelsBySubscribeUrls,
            "open_multicast": getChannelsByFOFA,
            "open_online_search": useAccessibleUrl,
        }
        for config_name, task_func in task_dict.items():
            if getattr(config, config_name):
                task = None
                if config_name == "open_subscribe":
                    task = asyncio.create_task(task_func(self.update_progress))
                elif config_name == "open_multicast":
                    task = asyncio.create_task(
                        task_func(self.driver, self.update_progress)
                    )
                else:
                    task = asyncio.create_task(task_func())
                if task:
                    self.tasks.append(task)
        task_results = await asyncio.gather(*self.tasks)
        self.tasks = []
        for i, config_name in enumerate(
            [name for name in task_dict if getattr(config, name)]
        ):
            self.results[config_name] = task_results[i]
        for cate, channel_obj in channel_items.items():
            channel_obj_keys = channel_obj.keys()
            for name in channel_obj_keys:
                await self.channel_queue.put((cate, name, channel_obj[name]))

    async def main(self):
        try:
            await self.visitPage(getChannelItems())
            for _ in range(10):
                channel_task = asyncio.create_task(self.process_channel())
                self.tasks.append(channel_task)
            self.total = self.channel_queue.qsize()
            self.pbar = tqdm(total=self.channel_queue.qsize())
            self.pbar.set_description(
                f"Processing..., {self.channel_queue.qsize()} channels remaining"
            )
            self.update_progress(f"正在更新...", int((self.pbar.n / self.total) * 100))
            tasks_with_progress = [
                self.run_task(task, self.pbar) for task in self.tasks
            ]
            await asyncio.gather(*tasks_with_progress)
            self.tasks = []
            self.pbar.close()
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
            self.update_progress(f"更新完成, 请检查{user_final_file}文件", 100)
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")

    def start(self, callback):
        self.update_progress = callback
        asyncio.run(self.main())

    def stop(self):
        for task in self.tasks:
            task.cancel()
