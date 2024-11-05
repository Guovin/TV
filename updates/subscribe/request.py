import utils.constants as constants
from tqdm.asyncio import tqdm_asyncio
from time import time
from requests import Session, exceptions
from utils.config import config
import utils.constants as constants
from utils.retry import retry_func
from utils.channel import get_name_url, format_channel_name
from utils.tools import (
    merge_objects,
    get_pbar_remaining,
    format_url_with_cache,
    add_url_info,
)
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict


async def get_channels_by_subscribe_urls(
    urls,
    multicast=False,
    hotel=False,
    retry=True,
    error_print=True,
    callback=None,
):
    """
    Get the channels by subscribe urls
    """
    subscribe_results = {}
    subscribe_urls_len = len(urls if urls else config.subscribe_urls)
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
    hotel_name = constants.origin_map["hotel"]
    multicast_name = constants.origin_map["multicast"]
    subscribe_name = constants.origin_map["subscribe"]

    def process_subscribe_channels(subscribe_info):
        if (multicast or hotel) and isinstance(subscribe_info, dict):
            region = subscribe_info.get("region")
            type = subscribe_info.get("type", "")
            subscribe_url = subscribe_info.get("url")
        else:
            subscribe_url = subscribe_info
        channels = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        try:
            response = None
            try:
                response = (
                    retry_func(
                        lambda: session.get(
                            subscribe_url, timeout=config.request_timeout
                        ),
                        name=subscribe_url,
                    )
                    if retry
                    else session.get(subscribe_url, timeout=config.request_timeout)
                )
            except exceptions.Timeout:
                print(f"Timeout on subscribe: {subscribe_url}")
            if response:
                response.encoding = "utf-8"
                content = response.text
                data = get_name_url(
                    content,
                    pattern=(
                        constants.m3u_pattern
                        if "#EXTM3U" in content
                        else constants.txt_pattern
                    ),
                    multiline=True,
                )
                for item in data:
                    name = item["name"]
                    url = item["url"]
                    if name and url:
                        url = url.partition("$")[0]
                        if not multicast:
                            info = (
                                f"{region}{hotel_name}"
                                if hotel
                                else (
                                    f"{multicast_name}"
                                    if "/rtp/" in url
                                    else f"{subscribe_name}"
                                )
                            )
                            url = add_url_info(url, info)
                        url = format_url_with_cache(
                            url, cache=subscribe_url if (multicast or hotel) else None
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
            for subscribe_url in (urls if urls else config.subscribe_urls)
        ]
        for future in futures:
            subscribe_results = merge_objects(subscribe_results, future.result())
    session.close()
    pbar.close()
    return subscribe_results
