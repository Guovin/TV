import asyncio
from utils.config import config
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
    return render_template_string("<pre>{{ content }}</pre>", content=content)


class UpdateSource:

    def __init__(self):
        self.run_ui = False
        self.tasks = []
        self.channel_items = get_channel_items()
        self.subscribe_result = {}
        self.multicast_result = {}
        self.online_search_result = {}
        self.channel_data = {}
        self.pbar = None
        self.total = 0
        self.start_time = None

    async def visit_page(self, channel_names=None):
        if config.getboolean("Settings", "open_subscribe"):
            subscribe_task = asyncio.create_task(
                get_channels_by_subscribe_urls(callback=self.update_progress)
            )
            self.tasks.append(subscribe_task)
            self.subscribe_result = await subscribe_task
        if config.getboolean("Settings", "open_multicast"):
            multicast_task = asyncio.create_task(
                get_channels_by_multicast(channel_names, self.update_progress)
            )
            self.tasks.append(multicast_task)
            self.multicast_result = await multicast_task
        if config.getboolean("Settings", "open_online_search"):
            online_search_task = asyncio.create_task(
                get_channels_by_online_search(channel_names, self.update_progress)
            )
            self.tasks.append(online_search_task)
            self.online_search_result = await online_search_task

    def pbar_update(self, name=""):
        self.pbar.update()
        self.update_progress(
            f"正在进行{name}, 剩余{self.pbar.total - self.pbar.n}个接口, 预计剩余时间: {get_pbar_remaining(self.pbar, self.start_time)}",
            int((self.pbar.n / self.total) * 100),
        )

    async def main(self):
        try:
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
                            lambda: self.pbar_update("测速排序"),
                        )
                    )
                    for cate, channel_obj in self.channel_data.items()
                    for name, info_list in channel_obj.items()
                ]
                self.pbar = tqdm_asyncio(total=len(self.tasks), desc="Sorting")
                self.update_progress(
                    f"正在测速排序, 共{len(self.tasks)}个频道",
                    int((self.pbar.n / len(self.tasks)) * 100),
                )
                self.start_time = time()
                sort_results = await tqdm_asyncio.gather(*self.tasks, disable=True)
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
                lambda: self.pbar_update("写入结果"),
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
        if config.getboolean("Settings", "open_update"):
            await self.main()
        if self.run_ui:
            if not config.getboolean("Settings", "open_update"):
                print(f"You can access the result at {get_ip_address()}")
                self.update_progress(
                    f"服务启动成功, 可访问以下链接:",
                    100,
                    True,
                    url=f"{get_ip_address()}",
                )
            app.run(host="0.0.0.0", port=8000)

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


if __name__ == "__main__":
    # Run scheduled_task
    scheduled_task()

    # If not run with 'scheduled_task' argument and not in GitHub Actions, start Flask server
    if len(sys.argv) <= 1 or sys.argv[1] != "scheduled_task":
        if not os.environ.get("GITHUB_ACTIONS"):
            app.run(host="0.0.0.0", port=3001)
