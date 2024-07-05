import asyncio
from utils import (
    get_channel_items,
    update_channel_urls_txt,
    update_file,
    sort_urls_by_speed_and_resolution,
    get_total_urls_from_info_list,
    get_channels_by_subscribe_urls,
    check_url_by_patterns,
    get_channels_by_fofa,
    get_channels_by_online_search,
    format_channel_name,
    resource_path,
    load_external_config,
    get_pbar_remaining,
    get_ip_address,
)
import logging
from logging.handlers import RotatingFileHandler
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from time import time
from flask import Flask, render_template_string
import sys

config_path = resource_path("user_config.py")
default_config_path = resource_path("config.py")
config = (
    load_external_config("user_config.py")
    if os.path.exists(config_path)
    else load_external_config("config.py")
)

app = Flask(__name__)


@app.route("/")
def show_result():
    user_final_file = getattr(config, "final_file", "result.txt")
    with open(user_final_file, "r", encoding="utf-8") as file:
        content = file.read()
    return render_template_string("<pre>{{ content }}</pre>", content=content)


class UpdateSource:

    def __init__(self):
        self.run_ui = False
        self.tasks = []
        self.channel_items = get_channel_items()
        self.results = {}
        self.channel_data = {}
        self.pbar = None
        self.total = 0
        self.start_time = None

    def check_info_data(self, cate, name):
        if self.channel_data.get(cate) is None:
            self.channel_data[cate] = {}
        if self.channel_data[cate].get(name) is None:
            self.channel_data[cate][name] = []

    def append_data_to_info_data(self, cate, name, data, check=True):
        self.check_info_data(cate, name)
        for url, date, resolution in data:
            if (url and not check) or (url and check and check_url_by_patterns(url)):
                self.channel_data[cate][name].append((url, date, resolution))

    async def sort_channel_list(self, cate, name, info_list):
        try:
            sorted_data = await sort_urls_by_speed_and_resolution(info_list)
            if sorted_data:
                self.check_info_data(cate, name)
                self.channel_data[cate][name] = []
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
                self.append_data_to_info_data(cate, name, data, False)
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            self.pbar.update()
            self.pbar.set_description(
                f"Sorting, {self.pbar.total - self.pbar.n} channels remaining"
            )
            self.update_progress(
                f"正在测速排序, 剩余{self.pbar.total - self.pbar.n}个频道, 预计剩余时间: {get_pbar_remaining(self.pbar, self.start_time)}",
                int((self.pbar.n / self.total) * 100),
            )

    def process_channel(self):
        for cate, channel_obj in self.channel_items.items():
            for name, old_urls in channel_obj.items():
                formatName = format_channel_name(name)
                if config.open_subscribe:
                    self.append_data_to_info_data(
                        cate, name, self.results["open_subscribe"].get(formatName, [])
                    )
                    print(
                        name,
                        "subscribe num:",
                        len(self.results["open_subscribe"].get(formatName, [])),
                    )
                if config.open_multicast:
                    self.append_data_to_info_data(
                        cate, name, self.results["open_multicast"].get(formatName, [])
                    )
                    print(
                        name,
                        "multicast num:",
                        len(self.results["open_multicast"].get(formatName, [])),
                    )
                if config.open_online_search:
                    self.append_data_to_info_data(
                        cate,
                        name,
                        self.results["open_online_search"].get(formatName, []),
                    )
                    print(
                        name,
                        "online search num:",
                        len(self.results["open_online_search"].get(formatName, [])),
                    )
                print(
                    name,
                    "total num:",
                    len(self.channel_data.get(cate, {}).get(name, [])),
                )
                if len(self.channel_data.get(cate, {}).get(name, [])) == 0:
                    self.append_data_to_info_data(
                        cate, name, [(url, None, None) for url in old_urls]
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
                    print("write:", cate, name, "num:", len(channel_urls))
                    update_channel_urls_txt(cate, name, channel_urls)
                finally:
                    self.pbar.update()
                    self.pbar.set_description(
                        f"Writing, {self.pbar.total - self.pbar.n} channels remaining"
                    )
                    self.update_progress(
                        f"正在写入结果, 剩余{self.pbar.total - self.pbar.n}个接口, 预计剩余时间: {get_pbar_remaining(self.pbar, self.start_time)}",
                        int((self.pbar.n / self.total) * 100),
                    )

    async def visit_page(self, channel_names=None):
        task_dict = {
            "open_subscribe": get_channels_by_subscribe_urls,
            "open_multicast": get_channels_by_fofa,
            "open_online_search": get_channels_by_online_search,
        }
        for config_name, task_func in task_dict.items():
            if getattr(config, config_name):
                task = None
                if config_name == "open_subscribe" or config_name == "open_multicast":
                    task = asyncio.create_task(task_func(self.update_progress))
                else:
                    task = asyncio.create_task(
                        task_func(channel_names, self.update_progress)
                    )
                if task:
                    self.tasks.append(task)
        task_results = await tqdm_asyncio.gather(*self.tasks, disable=True)
        self.tasks = []
        for i, config_name in enumerate(
            [name for name in task_dict if getattr(config, name)]
        ):
            self.results[config_name] = task_results[i]

    async def main(self):
        try:
            self.tasks = []
            channel_names = [
                name
                for channel_obj in self.channel_items.values()
                for name in channel_obj.keys()
            ]
            self.total = len(channel_names)
            await self.visit_page(channel_names)
            self.process_channel()
            if config.open_sort:
                self.tasks = [
                    asyncio.create_task(self.sort_channel_list(cate, name, info_list))
                    for cate, channel_obj in self.channel_data.items()
                    for name, info_list in channel_obj.items()
                ]
                self.pbar = tqdm_asyncio(total=len(self.tasks))
                self.pbar.set_description(
                    f"Sorting, {len(self.tasks)} channels remaining"
                )
                self.update_progress(
                    f"正在测速排序, 共{len(self.tasks)}个频道",
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
            update_file(user_final_file, "result_new.txt")
            if config.open_sort:
                user_log_file = (
                    "user_result.log"
                    if os.path.exists("user_config.py")
                    else "result.log"
                )
                update_file(user_log_file, "result_new.log")
            print(f"Update completed! Please check the {user_final_file} file!")
            if not os.environ.get("GITHUB_ACTIONS"):
                print(f"You can access the result at {get_ip_address()}")
            if self.run_ui:
                self.update_progress(
                    f"更新完成, 请检查{user_final_file}文件, 可访问以下链接:",
                    100,
                    True,
                    url=f"{get_ip_address()}",
                )
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")

    async def start(self, callback=None):
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
        await self.main()
        if self.run_ui:
            app.run(host="0.0.0.0", port=8000)

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        if self.pbar:
            self.pbar.close()


def scheduled_task():
    if config.open_update:
        update_source = UpdateSource()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_source.start())


if __name__ == "__main__":
    # Run scheduled_task
    scheduled_task()

    # If not run with 'scheduled_task' argument and not in GitHub Actions, start Flask server
    if len(sys.argv) <= 1 or sys.argv[1] != "scheduled_task":
        if not os.environ.get("GITHUB_ACTIONS"):
            app.run(host="0.0.0.0", port=3000)
