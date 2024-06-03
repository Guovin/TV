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
from time import time

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
        self.tasks = []
        self.results = {}
        self.channel_queue = asyncio.Queue()
        self.channel_data = {}
        self.pbar = None
        self.total = 0
        self.start_time = None

    def get_pbar_remaining(self):
        try:
            elapsed = time() - self.start_time
            completed_tasks = self.pbar.n
            if completed_tasks > 0:
                avg_time_per_task = elapsed / completed_tasks
                remaining_tasks = self.pbar.total - completed_tasks
                remaining_time = self.pbar.format_interval(
                    avg_time_per_task * remaining_tasks
                )
            else:
                remaining_time = "未知"
            return remaining_time
        except Exception as e:
            print(f"Error: {e}")

    def append_data_to_info_data(self, cate, name, data):
        for url, date, resolution in data:
            if url and checkUrlByPatterns(url):
                if self.channel_data.get(cate) is None:
                    self.channel_data[cate] = {}
                if self.channel_data[cate].get(name) is None:
                    self.channel_data[cate][name] = []
                self.channel_data[cate][name].append((url, date, resolution))

    async def sort_channel_list(self, cate, name, info_list):
        try:
            github_actions = os.environ.get("GITHUB_ACTIONS")
            if (
                config.open_sort
                and not github_actions
                or (self.pbar.n <= 200 and github_actions == "true")
            ):
                sorted_data = await sortUrlsBySpeedAndResolution(info_list)
                if sorted_data:
                    for (
                        url,
                        date,
                        resolution,
                    ), response_time in sorted_data:
                        logging.info(
                            f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                        )
                    data = [
                        (url, date, resolution)
                        for (url, date, resolution), _ in sorted_data
                    ]
                    self.append_data_to_info_data(cate, name, data)
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            self.pbar.update()
            self.pbar.set_description(
                f"Sorting, {self.pbar.total - self.pbar.n} urls remaining"
            )
            self.update_progress(
                f"正在排序, 剩余{self.pbar.total - self.pbar.n}个接口, 预计剩余时间: {self.get_pbar_remaining()}",
                int((self.pbar.n / self.total) * 100),
            )

    async def process_channel(self):
        try:
            cate, name, old_urls = await self.channel_queue.get()
            format_name = formatChannelName(name)
            if config.open_subscribe:
                self.append_data_to_info_data(
                    cate, name, self.results["open_subscribe"].get(format_name, [])
                )
            if config.open_multicast:
                self.append_data_to_info_data(
                    cate, name, self.results["open_multicast"].get(format_name, [])
                )
            if config.open_online_search and self.results["open_online_search"]:
                online_info_list = getChannelsInfoListByOnlineSearch(
                    self.driver, self.results["open_online_search"], format_name
                )
                if online_info_list:
                    self.append_data_to_info_data(cate, name, online_info_list)
            if len(self.channel_data.get(cate, {}).get(name, [])) == 0:
                self.append_data_to_info_data(
                    cate, name, [(url, None, None) for url in old_urls]
                )
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")
        finally:
            self.channel_queue.task_done()
            self.pbar.update()
            self.pbar.set_description(
                f"Processing, {self.channel_queue.qsize()} channels remaining"
            )
            self.update_progress(
                f"正在更新, 剩余{self.channel_queue.qsize()}个频道待处理, 预计剩余时间: {self.get_pbar_remaining()}",
                int((self.pbar.n / self.total) * 100),
            )

    async def write_channel_to_file(self):
        total = len(
            [
                name
                for channel_obj in self.channel_data.values()
                for name in channel_obj.keys()
            ]
        )
        self.pbar = tqdm_asyncio(total=total)
        self.pbar.set_description(f"Writing, {total} channels remaining")
        self.start_time = time()
        for cate, channel_obj in self.channel_data.items():
            for name, info_list in channel_obj.items():
                try:
                    channel_urls = getTotalUrlsFromInfoList(info_list)
                    await updateChannelUrlsTxt(cate, name, channel_urls)
                finally:
                    self.pbar.update()
                    self.pbar.set_description(
                        f"Writing, {self.pbar.total - self.pbar.n} channels remaining"
                    )
                    self.update_progress(
                        f"正在写入结果, 剩余{self.pbar.total - self.pbar.n}个接口, 预计剩余时间: {self.get_pbar_remaining()}",
                        int((self.pbar.n / self.total) * 100),
                    )

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
        task_results = await tqdm_asyncio.gather(*self.tasks, disable=True)
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
            self.tasks = []
            await self.visitPage(getChannelItems())
            self.total = self.channel_queue.qsize()
            self.tasks = [
                asyncio.create_task(self.process_channel()) for _ in range(self.total)
            ]
            self.pbar = tqdm_asyncio(total=self.total)
            self.pbar.set_description(f"Processing, {self.total} channels remaining")
            self.update_progress(
                f"正在更新, 共{self.total}个频道",
                int((self.pbar.n / self.total) * 100),
            )
            self.start_time = time()
            await tqdm_asyncio.gather(*self.tasks, disable=True)
            if config.open_sort:
                self.tasks = [
                    asyncio.create_task(self.sort_channel_list(cate, name, info_list))
                    for cate, channel_obj in self.channel_data.items()
                    for name, info_list in channel_obj.items()
                ]
                self.pbar = tqdm_asyncio(total=len(self.tasks))
                self.pbar.set_description(f"Sorting, {len(self.tasks)} urls remaining")
                self.update_progress(
                    f"正在排序, 共{len(self.tasks)}个接口",
                    int((self.pbar.n / len(self.tasks)) * 100),
                )
                self.start_time = time()
                self.channel_data = {}
                await tqdm_asyncio.gather(*self.tasks, disable=True)
            await self.write_channel_to_file()
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
            self.update_progress(f"更新完成, 请检查{user_final_file}文件", 100, True)
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
