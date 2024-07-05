from utils.config import get_config
from tqdm.asyncio import tqdm_asyncio
from time import time
from asyncio import Queue
from requests import get, exceptions
from utils.retry import retry_func
import re
from utils.channel import format_channel_name
from utils.utils import get_pbar_remaining
from concurrent.futures import ThreadPoolExecutor
from asyncio import get_running_loop


config = get_config()
timeout = 10


async def get_channels_by_subscribe_urls(callback):
    """
    Get the channels by subscribe urls
    """
    channels = {}
    pattern = r"^(.*?),(?!#genre#)(.*?)$"
    subscribe_urls_len = len(config.subscribe_urls)
    pbar = tqdm_asyncio(total=subscribe_urls_len)
    start_time = time()
    pbar.set_description(f"Processing subscribe, {subscribe_urls_len} urls remaining")
    callback(f"正在获取订阅源更新, 共{subscribe_urls_len}个订阅源", 0)
    subscribe_queue = Queue()
    for subscribe_url in config.subscribe_urls:
        await subscribe_queue.put(subscribe_url)

    def process_subscribe_channels(subscribe_url):
        try:
            response = None
            try:
                response = retry_func(
                    lambda: get(subscribe_url, timeout=timeout),
                    name=subscribe_url,
                )
            except exceptions.Timeout:
                print(f"Timeout on subscribe: {subscribe_url}")
            if response:
                content = response.text
                lines = content.split("\n")
                for line in lines:
                    matcher = re.match(pattern, line)
                    if matcher is not None:
                        key = matcher.group(1)
                        resolution_match = re.search(r"_(\((.*?)\))", key)
                        resolution = (
                            resolution_match.group(2)
                            if resolution_match is not None
                            else None
                        )
                        url = matcher.group(2)
                        value = (url, None, resolution)
                        name = format_channel_name(key)
                        if name in channels:
                            if value not in channels[name]:
                                channels[name].append(value)
                        else:
                            channels[name] = [value]
        except Exception as e:
            print(f"Error on {subscribe_url}: {e}")
        finally:
            subscribe_queue.task_done()
            pbar.update()
            remain = subscribe_urls_len - pbar.n
            pbar.set_description(f"Processing subscribe, {remain} urls remaining")
            callback(
                f"正在获取订阅源更新, 剩余{remain}个订阅源待获取, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / subscribe_urls_len) * 100),
            )
            if config.open_online_search and pbar.n / subscribe_urls_len == 1:
                callback("正在获取在线搜索结果, 请耐心等待", 0)

    with ThreadPoolExecutor(max_workers=5) as pool:
        loop = get_running_loop()
        subscribe_url = await subscribe_queue.get()
        loop.run_in_executor(pool, process_subscribe_channels, subscribe_url)
    print("Finished processing subscribe urls")
    pbar.close()
    return channels
