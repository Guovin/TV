from utils.config import get_config
from tqdm.asyncio import tqdm_asyncio
from time import time
from requests import Session, exceptions
from utils.retry import retry_func
import re
from utils.channel import format_channel_name
from utils.tools import merge_objects, get_pbar_remaining
from concurrent.futures import ThreadPoolExecutor


config = get_config()
timeout = 10


async def get_channels_by_subscribe_urls(callback):
    """
    Get the channels by subscribe urls
    """
    subscribe_results = {}
    pattern = r"^(.*?),(?!#genre#)(.*?)$"
    subscribe_urls_len = len(config.subscribe_urls)
    pbar = tqdm_asyncio(total=subscribe_urls_len, desc="Processing subscribe")
    start_time = time()
    callback(f"正在获取订阅源更新, 共{subscribe_urls_len}个订阅源", 0)
    session = Session()

    def process_subscribe_channels(subscribe_url):
        channels = {}
        try:
            response = None
            try:
                response = retry_func(
                    lambda: session.get(subscribe_url, timeout=timeout),
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
            pbar.update()
            remain = subscribe_urls_len - pbar.n
            callback(
                f"正在获取订阅源更新, 剩余{remain}个订阅源待获取, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / subscribe_urls_len) * 100),
            )
            if config.open_online_search and pbar.n / subscribe_urls_len == 1:
                callback("正在获取在线搜索结果, 请耐心等待", 0)
            return channels

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(process_subscribe_channels, subscribe_url)
            for subscribe_url in config.subscribe_urls
        ]
        for future in futures:
            merge_objects(subscribe_results, future.result())
    session.close()
    pbar.close()
    return subscribe_results
