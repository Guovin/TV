import asyncio
from utils.config import config
import utils.constants as constants
from utils.channel import (
    get_channel_items,
    append_total_data,
    process_sort_channel_list,
    write_channel_to_file,
    setup_logging,
    cleanup_logging,
    get_channel_data_cache_with_compare,
    format_channel_url_info,
)
from utils.tools import (
    update_file,
    get_pbar_remaining,
    get_ip_address,
    convert_to_m3u,
    get_result_file_content,
    process_nested_dict,
    format_interval,
    check_ipv6_support,
    resource_path,
)
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
import atexit
import pickle
import copy

app = Flask(__name__)

atexit.register(cleanup_logging)


@app.route("/")
def show_index():
    return get_result_file_content()


@app.route("/result")
def show_result():
    return get_result_file_content(show_result=True)


@app.route("/log")
def show_log():
    user_log_file = "output/" + (
        "user_result.log" if os.path.exists("config/user_config.ini") else "result.log"
    )
    if os.path.exists(user_log_file):
        with open(user_log_file, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        content = constants.waiting_tip
    return render_template_string(
        "<head><link rel='icon' href='{{ url_for('static', filename='images/favicon.ico') }}' type='image/x-icon'></head><pre>{{ content }}</pre>",
        content=content,
    )


class UpdateSource:

    def __init__(self):
        self.run_ui = False
        self.tasks = []
        self.channel_items = {}
        self.hotel_fofa_result = {}
        self.hotel_foodie_result = {}
        self.multicast_result = {}
        self.subscribe_result = {}
        self.online_search_result = {}
        self.channel_data = {}
        self.pbar = None
        self.total = 0
        self.start_time = None

    async def visit_page(self, channel_names=None):
        tasks_config = [
            ("hotel_fofa", get_channels_by_fofa, "hotel_fofa_result"),
            ("multicast", get_channels_by_multicast, "multicast_result"),
            ("hotel_foodie", get_channels_by_hotel, "hotel_foodie_result"),
            ("subscribe", get_channels_by_subscribe_urls, "subscribe_result"),
            (
                "online_search",
                get_channels_by_online_search,
                "online_search_result",
            ),
        ]

        for setting, task_func, result_attr in tasks_config:
            if (
                setting == "hotel_foodie" or setting == "hotel_fofa"
            ) and config.open_hotel == False:
                continue
            if config.open_method[setting]:
                if setting == "subscribe":
                    subscribe_urls = config.subscribe_urls
                    task = asyncio.create_task(
                        task_func(subscribe_urls, callback=self.update_progress)
                    )
                elif setting == "hotel_foodie" or setting == "hotel_fofa":
                    task = asyncio.create_task(task_func(callback=self.update_progress))
                else:
                    task = asyncio.create_task(
                        task_func(channel_names, callback=self.update_progress)
                    )
                self.tasks.append(task)
                setattr(self, result_attr, await task)

    def pbar_update(self, name=""):
        if self.pbar.n < self.total:
            self.pbar.update()
            self.update_progress(
                f"正在进行{name}, 剩余{self.total - self.pbar.n}个接口, 预计剩余时间: {get_pbar_remaining(n=self.pbar.n, total=self.total, start_time=self.start_time)}",
                int((self.pbar.n / self.total) * 100),
            )

    def get_urls_len(self, filter=False):
        data = copy.deepcopy(self.channel_data)
        if filter:
            process_nested_dict(data, seen=set(), flag=r"cache:(.*)", force_str="!")
        processed_urls = set(
            url_info[0]
            for channel_obj in data.values()
            for url_info_list in channel_obj.values()
            for url_info in url_info_list
        )
        return len(processed_urls)

    async def main(self):
        try:
            if config.open_update:
                setup_logging()
                main_start_time = time()
                self.channel_items = get_channel_items()
                channel_names = [
                    name
                    for channel_obj in self.channel_items.values()
                    for name in channel_obj.keys()
                ]
                await self.visit_page(channel_names)
                self.tasks = []
                append_total_data(
                    self.channel_items.items(),
                    channel_names,
                    self.channel_data,
                    self.hotel_fofa_result,
                    self.multicast_result,
                    self.hotel_foodie_result,
                    self.subscribe_result,
                    self.online_search_result,
                )
                channel_data_cache = copy.deepcopy(self.channel_data)
                ipv6_support = check_ipv6_support()
                open_sort = config.open_sort
                if open_sort:
                    urls_total = self.get_urls_len()
                    self.total = self.get_urls_len(filter=True)
                    print(f"Total urls: {urls_total}, need to sort: {self.total}")
                    sort_callback = lambda: self.pbar_update(name="测速")
                    self.update_progress(
                        f"正在测速排序, 共{urls_total}个接口, {self.total}个接口需要进行测速",
                        0,
                    )
                    self.start_time = time()
                    self.pbar = tqdm_asyncio(total=self.total, desc="Sorting")
                    self.channel_data = await process_sort_channel_list(
                        self.channel_data,
                        ipv6=ipv6_support,
                        callback=sort_callback,
                    )
                else:
                    format_channel_url_info(self.channel_data)
                self.total = self.get_urls_len()
                self.pbar = tqdm(total=self.total, desc="Writing")
                self.start_time = time()
                write_channel_to_file(
                    self.channel_data,
                    ipv6=ipv6_support,
                    callback=lambda: self.pbar_update(name="写入结果"),
                )
                self.pbar.close()
                user_final_file = config.final_file
                update_file(user_final_file, "output/result_new.txt")
                if config.open_use_old_result:
                    if open_sort:
                        get_channel_data_cache_with_compare(
                            channel_data_cache, self.channel_data
                        )
                    with open(
                        resource_path("output/result_cache.pkl", persistent=True), "wb"
                    ) as file:
                        pickle.dump(channel_data_cache, file)
                if open_sort:
                    user_log_file = "output/" + (
                        "user_result.log"
                        if os.path.exists("config/user_config.ini")
                        else "result.log"
                    )
                    update_file(user_log_file, "output/result_new.log", copy=True)
                    cleanup_logging()
                convert_to_m3u()
                total_time = format_interval(time() - main_start_time)
                print(
                    f"🥳 Update completed! Total time spent: {total_time}. Please check the {user_final_file} file!"
                )
            open_service = config.open_service
            if self.run_ui:
                service_tip = ", 可使用以下链接观看直播:" if open_service else ""
                tip = (
                    f"✅ 服务启动成功{service_tip}"
                    if open_service and config.open_update == False
                    else f"🥳 更新完成, 耗时: {total_time}, 请检查{user_final_file}文件{service_tip}"
                )
                self.update_progress(
                    tip,
                    100,
                    True,
                    url=f"{get_ip_address()}" if open_service else None,
                )
        except asyncio.exceptions.CancelledError:
            print("Update cancelled!")

    async def start(self, callback=None):
        def default_callback(self, *args, **kwargs):
            pass

        self.update_progress = callback or default_callback
        self.run_ui = True if callback else False
        await self.main()

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        if self.pbar:
            self.pbar.close()


def scheduled_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    update_source = UpdateSource()
    loop.run_until_complete(update_source.start())


def run_service():
    try:
        if not os.environ.get("GITHUB_ACTIONS"):
            ip_address = get_ip_address()
            print(f"📄 Result detail: {ip_address}/result")
            print(f"📄 Log detail: {ip_address}/log")
            print(f"✅ You can use this url to watch IPTV 📺: {ip_address}")
            app.run(host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"❌ Service start failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1 and config.open_service:
        loop = asyncio.new_event_loop()

        async def run_service_async():
            loop.run_in_executor(None, run_service)

        asyncio.run(run_service_async())
    scheduled_task()
