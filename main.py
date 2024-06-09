import asyncio
from utils import (
    get_channel_items,
    update_channel_urls_txt,
    update_file,
    sort_urls_by_speed_and_resolution,
    get_total_urls_from_info_list,
    use_accessible_url,
    get_channels_by_subscribe_urls,
    check_url_by_patterns,
    get_channels_by_fofa,
    async_get_channels_info_list_by_online_search,
    format_channel_name,
    resource_path,
    load_external_config,
)
import logging
from logging.handlers import RotatingFileHandler
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import threading
from time import time

config_path = resource_path("user_config.py")
default_config_path = resource_path("config.py")
config = (
    load_external_config("user_config.py")
    if os.path.exists(config_path)
    else load_external_config("config.py")
)


class UpdateSource:

    def __init__(self):
        self.run_ui = False
        self.thread = None
        self.tasks = []
        self.channel_items = get_channel_items()
        self.results = {}
        self.channel_queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(10)
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
            if url and check_url_by_patterns(url):
                if self.channel_data.get(cate) is None:
                    self.channel_data[cate] = {}
                if self.channel_data[cate].get(name) is None:
                    self.channel_data[cate][name] = []
                self.channel_data[cate][name].append((url, date, resolution))

    async def sort_channel_list(self, cate, name, info_list):
        try:
            if config.open_sort:
                sorted_data = await sort_urls_by_speed_and_resolution(info_list)
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
                f"正在测速排序, 剩余{self.pbar.total - self.pbar.n}个接口, 预计剩余时间: {self.get_pbar_remaining()}",
                int((self.pbar.n / self.total) * 100),
            )

    async def process_channel(self):
        async with self.semaphore:
            try:
                cate, name, old_urls = await self.channel_queue.get()
                format_name = format_channel_name(name)
                if config.open_subscribe:
                    self.append_data_to_info_data(
                        cate, name, self.results["open_subscribe"].get(format_name, [])
                    )
                if config.open_multicast:
                    self.append_data_to_info_data(
                        cate, name, self.results["open_multicast"].get(format_name, [])
                    )
                if config.open_online_search and self.results["open_online_search"]:
                    online_info_list = (
                        await async_get_channels_info_list_by_online_search(
                            self.results["open_online_search"],
                            format_name,
                        )
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
                    f"Processing, {self.total - self.pbar.n} channels remaining"
                )
                self.update_progress(
                    f"正在更新, 剩余{self.total - self.pbar.n}个频道待处理, 预计剩余时间: {self.get_pbar_remaining()}",
                    int((self.pbar.n / self.total) * 100),
                )

    def write_channel_to_file(self):
        self.pbar = tqdm(total=self.total)
        self.pbar.set_description(f"Writing, {self.total} channels remaining")
        self.start_time = time()
        for cate, channel_obj in self.channel_items.items():
            for name in channel_obj.keys():
                info_list = self.channel_data.get(cate, {}).get(name, [])
                try:
                    channel_urls = get_total_urls_from_info_list(info_list)
                    update_channel_urls_txt(cate, name, channel_urls)
                finally:
                    self.pbar.update()
                    self.pbar.set_description(
                        f"Writing, {self.pbar.total - self.pbar.n} channels remaining"
                    )
                    self.update_progress(
                        f"正在写入结果, 剩余{self.pbar.total - self.pbar.n}个接口, 预计剩余时间: {self.get_pbar_remaining()}",
                        int((self.pbar.n / self.total) * 100),
                    )

    async def visit_page(self):
        task_dict = {
            "open_subscribe": get_channels_by_subscribe_urls,
            "open_multicast": get_channels_by_fofa,
            "open_online_search": use_accessible_url,
        }
        for config_name, task_func in task_dict.items():
            if getattr(config, config_name):
                task = None
                if config_name == "open_subscribe":
                    task = asyncio.create_task(task_func(self.update_progress))
                elif config_name == "open_multicast":
                    task = asyncio.create_task(task_func(self.update_progress))
                else:
                    task = asyncio.create_task(task_func(self.update_progress))
                if task:
                    self.tasks.append(task)
        task_results = await tqdm_asyncio.gather(*self.tasks, disable=True)
        self.tasks = []
        for i, config_name in enumerate(
            [name for name in task_dict if getattr(config, name)]
        ):
            self.results[config_name] = task_results[i]
        for cate, channel_obj in self.channel_items.items():
            for name in channel_obj.keys():
                await self.channel_queue.put((cate, name, channel_obj[name]))

    async def main(self):
        try:
            self.tasks = []
            await self.visit_page()
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
                    f"正在测速排序, 共{len(self.tasks)}个接口",
                    int((self.pbar.n / len(self.tasks)) * 100),
                )
                self.start_time = time()
                self.channel_data = {}
                await tqdm_asyncio.gather(*self.tasks, disable=True)
            self.write_channel_to_file()
            self.pbar.close()
            for handler in logging.root.handlers[:]:
                handler.close()
                logging.root.removeHandler(handler)
            user_final_file = getattr(config, "final_file", "result.txt")
            user_log_file = (
                "user_result.log" if os.path.exists("user_config.py") else "result.log"
            )
            update_file(user_final_file, "result_new.txt")
            update_file(user_log_file, "result_new.log")
            print(f"Update completed! Please check the {user_final_file} file!")
            self.update_progress(f"更新完成, 请检查{user_final_file}文件", 100, True)
            self.stop()
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")

    def start(self, callback=None):
        def default_callback(self, *args, **kwargs):
            pass

        self.update_progress = callback or default_callback
        self.run_ui = True if callback else False
        handler = RotatingFileHandler("result_new.log", encoding="utf-8")
        logging.basicConfig(
            handlers=[handler],
            format="%(message)s",
            level=logging.INFO,
        )

        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.main())
            finally:
                loop.close()

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        if not self.run_ui:
            self.thread.join()

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    update_source = UpdateSource()
    update_source.start()
