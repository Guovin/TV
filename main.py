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
from tqdm.asyncio import tqdm_asyncio
import threading

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
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        driver = webdriver.Chrome(options=options)
        return driver

    def __init__(self):
        self.driver = self.setup_driver()
        self.threads = []
        self.tasks = []
        self.results = {}
        self.channel_queue = asyncio.Queue()
        self.pbar = None
        self.total = 0
        self.lock = asyncio.Lock()

    def append_data_to_info_list(urls, info_list):
        for url, _, resolution in urls:
            if url and checkUrlByPatterns(url):
                info_list.append((url, None, resolution))

    async def process_channel(self):
        # while not self.channel_queue.empty():
        try:
            # print(1313)
            cate, name, old_urls = await self.channel_queue.get()
            # print(cate, name, old_urls)
            channel_urls = []
            format_name = formatChannelName(name)
            info_list = []
            if config.open_subscribe:
                self.append_data_to_info_list(
                    self.results["open_subscribe"].get(format_name, []),
                    info_list,
                )
            if config.open_multicast:
                self.append_data_to_info_list(
                    self.results["open_multicast"].get(format_name, []),
                    info_list,
                )
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
                    print(666, info_list)
                    sorted_data = await sortUrlsBySpeedAndResolution(info_list)
                    print(777, sorted_data)
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
                logging.error(f"Error: {e}")
            finally:
                print(8888, cate, name, channel_urls)
                await updateChannelUrlsTxt(cate, name, channel_urls)
                self.channel_queue.task_done()
                async with self.lock:
                    self.pbar.update()
                    self.pbar.set_description(
                        f"Processing..., {self.channel_queue.qsize()} channels remaining"
                    )
                    self.update_progress(
                        f"正在更新...", int((self.pbar.n / self.total) * 100)
                    )
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")

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
        task_results = await tqdm_asyncio.gather(*self.tasks)
        self.tasks = []
        for i, config_name in enumerate(
            [name for name in task_dict if getattr(config, name)]
        ):
            self.results[config_name] = task_results[i]
        for cate, channel_obj in channel_items.items():
            channel_obj_keys = channel_obj.keys()
            for name in channel_obj_keys:
                await self.channel_queue.put((cate, name, channel_obj[name]))

    async def thread_process_channel(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [asyncio.create_task(self.process_channel()) for _ in range(10)]
        self.tasks.extend(tasks)
        loop.run_until_complete(await tqdm_asyncio.gather(*tasks))
        loop.close()

    async def main(self):
        try:
            self.tasks = []
            await self.visitPage(getChannelItems())
            self.tasks = [
                asyncio.create_task(self.process_channel())
                for _ in range(self.channel_queue.qsize())
            ]
            self.total = self.channel_queue.qsize()
            self.pbar = tqdm_asyncio(total=self.channel_queue.qsize())
            self.pbar.set_description(
                f"Processing..., {self.channel_queue.qsize()} channels remaining"
            )
            self.update_progress(f"正在更新...", int((self.pbar.n / self.total) * 100))
            # for _ in range(10):
            #     loop = asyncio.new_event_loop()
            #     asyncio.set_event_loop(loop)
            #     thread = threading.Thread(
            #         target=loop.run_until_complete,
            #         args=(self.thread_process_channel(),),
            #     )
            #     thread.start()
            #     self.threads.append(thread)
            # for thread in self.threads:
            #     thread.join()
            await tqdm_asyncio.gather(*self.tasks)
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
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        thread = threading.Thread(target=loop.run_until_complete, args=(self.main(),))
        thread.start()

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        asyncio.get_event_loop().stop()
