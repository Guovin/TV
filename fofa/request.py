from utils.config import get_config
from tqdm.asyncio import tqdm_asyncio
from time import time
from asyncio import Queue, get_running_loop
from requests import get
from concurrent.futures import ThreadPoolExecutor
import fofa_map
from driver.setup import setup_driver
import re
from utils.retry import retry_func
from utils.channel import format_channel_name
from utils.utils import merge_objects, get_pbar_remaining
from proxy import get_proxy

config = get_config()
timeout = 10


def get_fofa_urls_from_region_list():
    """
    Get the FOFA url from region
    """
    region_list = getattr(config, "region_list", [])
    urls = []
    region_url = getattr(fofa_map, "region_url")
    if "all" in region_list:
        urls = [url for url in region_url.values() if url]
    else:
        for region in region_list:
            if region in region_url:
                urls.append(region_url[region])
    return urls


async def get_channels_by_fofa(callback):
    """
    Get the channel by FOFA
    """
    fofa_urls = get_fofa_urls_from_region_list()
    fofa_urls_len = len(fofa_urls)
    pbar = tqdm_asyncio(total=fofa_urls_len, desc="Processing multicast")
    start_time = time()
    fofa_results = {}
    callback(f"正在获取组播源更新, 共{fofa_urls_len}个地区", 0)
    fofa_queue = Queue()
    for fofa_url in fofa_urls:
        await fofa_queue.put(fofa_url)
    proxy = None
    if config.open_proxy:
        proxy = await get_proxy(fofa_urls[0], best=True, with_test=True)
    driver = setup_driver(proxy)

    def process_fofa_channels(fofa_url, fofa_urls_len, proxy=None):
        # driver = None
        try:
            # driver = setup_driver(proxy)
            retry_func(lambda: driver.get(fofa_url), name=fofa_url)
            fofa_source = re.sub(r"<!--.*?-->", "", driver.page_source, flags=re.DOTALL)
            urls = set(re.findall(r"https?://[\w\.-]+:\d+", fofa_source))
            channels = {}
            for url in urls:
                try:
                    final_url = url + "/iptv/live/1000.json?key=txiptv"
                    # response = retry_func(
                    #     lambda: get(final_url, timeout=timeout),
                    #     name=final_url,
                    # )
                    response = get(final_url, timeout=timeout)
                    try:
                        json_data = response.json()
                        if json_data["code"] == 0:
                            try:
                                for item in json_data["data"]:
                                    if isinstance(item, dict):
                                        item_name = format_channel_name(
                                            item.get("name")
                                        )
                                        item_url = item.get("url").strip()
                                        if item_name and item_url:
                                            total_url = url + item_url
                                            if item_name not in channels:
                                                channels[item_name] = [total_url]
                                            else:
                                                channels[item_name].append(total_url)
                            except Exception as e:
                                # print(f"Error on fofa: {e}")
                                continue
                    except Exception as e:
                        # print(f"{url}: {e}")
                        continue
                except Exception as e:
                    # print(f"{url}: {e}")
                    continue
            merge_objects(fofa_results, channels)
        except Exception as e:
            print(e)
        finally:
            # if driver:
            #     driver.quit()
            fofa_queue.task_done()
            pbar.update()
            remain = fofa_urls_len - pbar.n
            callback(
                f"正在获取组播源更新, 剩余{remain}个地区待获取, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / fofa_urls_len) * 100),
            )
            if config.open_online_search and pbar.n / fofa_urls_len == 1:
                callback("正在获取在线搜索结果, 请耐心等待", 0)

    # with ThreadPoolExecutor(max_workers=5) as pool:
    while not fofa_queue.empty():
        # loop = get_running_loop()
        fofa_url = await fofa_queue.get()
        process_fofa_channels(fofa_url, fofa_urls_len, proxy)
        # loop.run_in_executor(
        #     pool, process_fofa_channels, fofa_url, fofa_urls_len, proxy
        # )
    driver.quit()
    pbar.close()
    return fofa_results
