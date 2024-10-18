from utils.config import config
from tqdm.asyncio import tqdm_asyncio
from time import time
from requests import Session, exceptions
from utils.retry import retry_func
from utils.channel import get_name_url, format_channel_name
from utils.tools import merge_objects, get_pbar_remaining, format_url_with_cache
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

timeout = config.getint("Settings", "request_timeout", fallback=10)


async def get_channels_by_subscribe_urls(
    urls,
    multicast=False,
    hotel=False,
    retry=True,
    error_print=True,
    with_cache=False,
    callback=None,
):
    """
    Get the channels by subscribe urls
    """
    subscribe_results = {}
    subscribe_urls = [
        url.strip()
        for url in config.get("Settings", "subscribe_urls", fallback="").split(",")
        if url.strip()
    ]
    subscribe_urls_len = len(urls if urls else subscribe_urls)
    pbar = tqdm_asyncio(
        total=subscribe_urls_len,
        desc=f"Processing subscribe {'for multicast' if multicast else ''}",
    )
    start_time = time()
    mode_name = "组播" if multicast else "酒店" if hotel else "订阅"
    if callback:
        callback(
            f"正在获取{mode_name}源, 共{subscribe_urls_len}个{mode_name}源",
            0,
        )
    session = Session()

    def process_subscribe_channels(subscribe_info):
        if multicast and isinstance(subscribe_info, dict):
            region = subscribe_info.get("region")
            type = subscribe_info.get("type")
            subscribe_url = subscribe_info.get("url")
        else:
            subscribe_url = subscribe_info
        channels = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        try:
            response = None
            try:
                response = (
                    retry_func(
                        lambda: session.get(subscribe_url, timeout=timeout),
                        name=subscribe_url,
                    )
                    if retry
                    else session.get(subscribe_url, timeout=timeout)
                )
            except exceptions.Timeout:
                print(f"Timeout on subscribe: {subscribe_url}")
            if response:
                response.encoding = "utf-8"
                content = response.text
                data = get_name_url(content)
                for item in data:
                    name = item["name"]
                    url = item["url"]
                    if name and url:
                        url = format_url_with_cache(
                            url, cache=subscribe_url if with_cache else None
                        )
                        value = url if multicast else (url, None, None)
                        name = format_channel_name(name)
                        if name in channels:
                            if multicast:
                                if value not in channels[name][region][type]:
                                    channels[name][region][type].append(value)
                            elif value not in channels[name]:
                                channels[name].append(value)
                        else:
                            if multicast:
                                channels[name][region][type] = [value]
                            else:
                                channels[name] = [value]
        except Exception as e:
            if error_print:
                print(f"Error on {subscribe_url}: {e}")
        finally:
            pbar.update()
            remain = subscribe_urls_len - pbar.n
            if callback:
                callback(
                    f"正在获取{mode_name}源, 剩余{remain}个{mode_name}源待获取, 预计剩余时间: {get_pbar_remaining(n=pbar.n, total=pbar.total, start_time=start_time)}",
                    int((pbar.n / subscribe_urls_len) * 100),
                )
            return channels

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(process_subscribe_channels, subscribe_url)
            for subscribe_url in (urls if urls else subscribe_urls)
        ]
        for future in futures:
            subscribe_results = merge_objects(subscribe_results, future.result())
    session.close()
    pbar.close()
    return subscribe_results
