import asyncio
from utils.config import config, copy_config
from utils.channel import (
    get_channel_items,
    append_data_to_info_data,
    append_total_data,
    sort_channel_list,
    write_channel_to_file,
)
from utils.tools import (
    update_file,
    get_pbar_remaining,
    get_ip_address,
)
from utils.speed import is_ffmpeg_installed
from updates.subscribe import get_channels_by_subscribe_urls
from updates.multicast import get_channels_by_multicast
from updates.hotel import get_channels_by_hotel
from updates.fofa import get_channels_by_fofa
from updates.online_search import get_channels_by_online_search
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from time import time
from flask import Flask, render_template_string
import sys
import shutil

app = Flask(__name__)


@app.route("/")
def show_result():
    user_final_file = config.get("Settings", "final_file")
    with open(user_final_file, "r", encoding="utf-8") as file:
        content = file.read()
    return render_template_string(
        "<head><link rel='icon' href='{{ url_for('static', filename='images/favicon.ico') }}' type='image/x-icon'></head><pre>{{ content }}</pre>",
        content=content,
    )


@app.route("/log")
def show_log():
    user_log_file = "output/" + (
        "user_result.log" if os.path.exists("config/user_config.ini") else "result.log"
    )
    with open(user_log_file, "r", encoding="utf-8") as file:
        content = file.read()
    return render_template_string(
        "<head><link rel='icon' href='{{ url_for('static', filename='images/favicon.ico') }}' type='image/x-icon'></head><pre>{{ content }}</pre>",
        content=content,
    )


class UpdateSource:

    def __init__(self):
        self.run_ui = False
        self.tasks = []
        self.channel_items = {}
        self.subscribe_result = {}
        self.multicast_result = {}
        self.hotel_tonkiang_result = {}
        self.hotel_fofa_result = {}
        self.online_search_result = {}
        self.channel_data = {}
        self.pbar = None
        self.total = 0
        self.start_time = None
        self.sort_n = 0

    async def visit_page(self, channel_names=None):
        tasks_config = [
            ("open_subscribe", get_channels_by_subscribe_urls, "subscribe_result"),
            ("open_multicast", get_channels_by_multicast, "multicast_result"),
            ("open_hotel_tonkiang", get_channels_by_hotel, "hotel_tonkiang_result"),
            ("open_hotel_fofa", get_channels_by_fofa, "hotel_fofa_result"),
            (
                "open_online_search",
                get_channels_by_online_search,
                "online_search_result",
            ),
        ]

        for setting, task_func, result_attr in tasks_config:
            if (
                setting == "open_hotel_tonkiang" or setting == "open_hotel_fofa"
            ) and config.getboolean("Settings", "open_hotel") == False:
                continue
            if config.getboolean("Settings", setting):
                task = asyncio.create_task(
                    task_func(channel_names, self.update_progress)
                )
                self.tasks.append(task)
                setattr(self, result_attr, await task)

    def pbar_update(self, name="", n=0):
        if not n:
            self.pbar.update()
        self.update_progress(
            f"正在进行{name}, 剩余{self.total - (n or self.pbar.n)}个频道, 预计剩余时间: {get_pbar_remaining(n=(n or self.pbar.n), total=self.total, start_time=self.start_time)}",
            int(((n or self.pbar.n) / self.total) * 100),
        )

    def sort_pbar_update(self):
        self.sort_n += 1
        self.pbar_update(name="测速", n=self.sort_n)

    async def main(self):
        try:
            self.channel_items = get_channel_items()
            if self.run_ui:
                copy_config()
            channel_names = [
                name
                for channel_obj in self.channel_items.values()
                for name in channel_obj.keys()
            ]
            self.total = len(channel_names)
            await self.visit_page(channel_names)
            self.tasks = []
            self.channel_data = append_total_data(
                self.channel_items.items(),
                self.channel_data,
                self.subscribe_result,
                self.multicast_result,
                self.hotel_tonkiang_result,
                self.hotel_fofa_result,
                self.online_search_result,
            )
            if config.getboolean("Settings", "open_sort"):
                is_ffmpeg = is_ffmpeg_installed()
                if not is_ffmpeg:
                    print("FFmpeg is not installed, using requests for sorting.")
                semaphore = asyncio.Semaphore(1 if is_ffmpeg else 100)
                self.tasks = [
                    asyncio.create_task(
                        sort_channel_list(
                            semaphore,
                            cate,
                            name,
                            info_list,
                            is_ffmpeg,
                            lambda: self.sort_pbar_update(),
                        )
                    )
                    for cate, channel_obj in self.channel_data.items()
                    for name, info_list in channel_obj.items()
                ]
                self.update_progress(
                    f"正在测速排序, 共{len(self.tasks)}个频道",
                    0,
                )
                self.start_time = time()
                self.pbar = tqdm_asyncio(total=len(self.tasks), desc="Sorting")
                sort_results = await tqdm_asyncio.gather(*self.tasks, desc="Sorting")
                self.channel_data = {}
                for result in sort_results:
                    if result:
                        cate = result.get("cate")
                        name = result.get("name")
                        data = result.get("data")
                        self.channel_data = append_data_to_info_data(
                            self.channel_data, cate, name, data, False
                        )
            self.pbar = tqdm(total=self.total, desc="Writing")
            self.start_time = time()
            write_channel_to_file(
                self.channel_items.items(),
                self.channel_data,
                lambda: self.pbar_update(name="写入结果"),
            )
            self.pbar.close()
            user_final_file = config.get("Settings", "final_file")
            update_file(user_final_file, "output/result_new.txt")
            if os.path.exists(user_final_file):
                result_file = (
                    "user_result.txt"
                    if os.path.exists("config/user_config.ini")
                    else "result.txt"
                )
                shutil.copy(user_final_file, result_file)
            if config.getboolean("Settings", "open_sort"):
                user_log_file = "output/" + (
                    "user_result.log"
                    if os.path.exists("config/user_config.ini")
                    else "result.log"
                )
                update_file(user_log_file, "output/result_new.log")
            print(f"Update completed! Please check the {user_final_file} file!")
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
        if config.getboolean("Settings", "open_update"):
            await self.main()
        if self.run_ui and config.getboolean("Settings", "open_update") == False:
            self.update_progress(
                f"服务启动成功, 可访问以下链接:",
                100,
                True,
                url=f"{get_ip_address()}",
            )
            run_app()

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        if self.pbar:
            self.pbar.close()


def scheduled_task():
    if config.getboolean("Settings", "open_update"):
        update_source = UpdateSource()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_source.start())


def run_app():
    if not os.environ.get("GITHUB_ACTIONS"):
        print(f"You can access the result at {get_ip_address()}")
        app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "scheduled_task"):
        scheduled_task()
    run_app()
