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
import threading
from queue import Queue

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
        self.stop_event = threading.Event()
        self.tasks = []
        self.results = {}
        self.channel_queue = Queue()
        self.lock = asyncio.Lock()

    async def process_channel(self):
        while True:
            cate, name, old_urls = self.channel_queue.get()
            channel_urls = []
            # pbar.set_description(
            #     f"Processing {name}, {total_channels - pbar.n} channels remaining"
            # )
            # if pbar.n == 0:
            #     self.update_progress(f"正在处理频道: {name}", 0)
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
                    or github_actions == "true"
                    # or (pbar.n <= 200 and github_actions == "true")
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
            except Exception as e:
                print(e)
            # finally:
            #     pbar.update()
            #     self.update_progress(
            #         f"正在处理频道: {name}", int((pbar.n / total_channels) * 100)
            #     )
            await updateChannelUrlsTxt(self.lock, cate, name, channel_urls)
            self.channel_queue.task_done()

    async def visitPage(self, channel_items):
        # channel_names = [
        #     name
        #     for _, channel_obj in channel_items.items()
        #     for name in channel_obj.keys()
        # ]
        task_dict = {
            "open_subscribe": getChannelsBySubscribeUrls,
            "open_multicast": getChannelsByFOFA,
            "open_online_search": useAccessibleUrl,
        }
        tasks = []
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
                    task = asyncio.create_task(task_func)
                tasks.append(task)
        task_results = await asyncio.gather(*tasks)
        for i, config_name in enumerate(
            [name for name in task_dict if getattr(config, name)]
        ):
            self.results[config_name] = task_results[i]
        # total_channels = len(channel_names)
        # pbar = tqdm(total=total_channels)
        for cate, channel_obj in channel_items.items():
            channel_obj_keys = channel_obj.keys()
            for name in channel_obj_keys:
                self.channel_queue.put((cate, name, channel_obj[name]))
        # pbar.close()

    async def main(self):
        try:
            task = asyncio.create_task(self.visitPage(getChannelItems()))
            self.tasks.append(task)
            await task
            for _ in range(10):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                channel_thread = threading.Thread(
                    target=loop.run_until_complete, args=(self.process_channel(),)
                )
                channel_thread.start()
            self.channel_queue.join()
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        thread = threading.Thread(target=loop.run_until_complete, args=(self.main(),))
        thread.start()

    def stop(self):
        self.stop_event.set()
        for task in self.tasks:
            task.cancel()
        self.stop_event.clear()
