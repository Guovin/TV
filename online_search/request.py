from asyncio import create_task, gather
from utils.speed import get_speed
from utils.channel import format_channel_name
from utils.utils import (
    check_url_by_patterns,
    get_pbar_remaining,
    get_results_from_soup,
)
from utils.config import get_config
from proxy import get_proxy
from time import time, sleep
from driver.setup import setup_driver
from utils.retry import (
    retry_func,
    locate_element_with_retry,
    find_clickable_element_with_retry,
)
from selenium.webdriver.common.by import By
import re
from bs4 import BeautifulSoup
from asyncio import Queue, get_running_loop
from tqdm.asyncio import tqdm_asyncio
from concurrent.futures import ThreadPoolExecutor

config = get_config()


async def use_accessible_url(callback):
    """
    Check if the url is accessible
    """
    callback(f"正在获取最优的在线检索节点", 0)
    baseUrl1 = "https://www.foodieguide.com/iptvsearch/"
    baseUrl2 = "http://tonkiang.us/"
    task1 = create_task(get_speed(baseUrl1, timeout=30))
    task2 = create_task(get_speed(baseUrl2, timeout=30))
    task_results = await gather(task1, task2)
    callback(f"获取在线检索节点完成", 100)
    if task_results[0] == float("inf") and task_results[1] == float("inf"):
        return None
    if task_results[0] < task_results[1]:
        return baseUrl1
    else:
        return baseUrl2


async def get_channels_by_online_search(names, callback):
    """
    Get the channels by online search
    """
    channels = {}
    pageUrl = await use_accessible_url(callback)
    if not pageUrl:
        return channels
    proxy = None
    if config.open_proxy:
        proxy = await get_proxy(pageUrl, best=True, with_test=True)
    start_time = time()
    driver = setup_driver(proxy)

    def process_channel_by_online_search(name, proxy=None):
        info_list = []
        # driver = None
        try:
            # driver = setup_driver(proxy)
            retry_func(lambda: driver.get(pageUrl), name=f"online search:{name}")
            search_box = locate_element_with_retry(
                driver, (By.XPATH, '//input[@type="text"]')
            )
            if not search_box:
                return
            search_box.clear()
            search_box.send_keys(name)
            submit_button = find_clickable_element_with_retry(
                driver, (By.XPATH, '//input[@type="submit"]')
            )
            if not submit_button:
                return
            sleep(3)
            driver.execute_script("arguments[0].click();", submit_button)
            isFavorite = name in config.favorite_list
            pageNum = (
                config.favorite_page_num if isFavorite else config.default_page_num
            )
            retry_limit = 3
            for page in range(1, pageNum + 1):
                retries = 0
                while retries < retry_limit:
                    try:
                        if page > 1:
                            page_link = find_clickable_element_with_retry(
                                driver,
                                (
                                    By.XPATH,
                                    f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                ),
                            )
                            if not page_link:
                                break
                            sleep(3)
                            driver.execute_script("arguments[0].click();", page_link)
                        sleep(3)
                        source = re.sub(
                            r"<!--.*?-->",
                            "",
                            driver.page_source,
                            flags=re.DOTALL,
                        )
                        soup = BeautifulSoup(source, "html.parser")
                        if soup:
                            results = get_results_from_soup(soup, name)
                            print(name, "page:", page, "results num:", len(results))
                            if len(results) == 0 and retries < retry_limit - 1:
                                print(
                                    f"{name}:No results found, refreshing page and retrying..."
                                )
                                driver.refresh()
                                retries += 1
                                continue
                            for result in results:
                                url, date, resolution = result
                                if url and check_url_by_patterns(url):
                                    info_list.append((url, date, resolution))
                            break
                        else:
                            print(
                                f"{name}:No results found, refreshing page and retrying..."
                            )
                            driver.refresh()
                            retries += 1
                            continue
                    except Exception as e:
                        print(f"{name}:Error on page {page}: {e}")
                        break
                if retries == retry_limit:
                    print(f"{name}:Reached retry limit, moving to next page")
        except Exception as e:
            print(f"{name}:Error on search: {e}")
            pass
        finally:
            # if driver:
            #     driver.quit()
            channels[format_channel_name(name)] = info_list
            names_queue.task_done()
            pbar.update()
            callback(
                f"正在线上查询更新, 剩余{names_len - pbar.n}个频道待查询, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / names_len) * 100),
            )

    names_queue = Queue()
    for name in names:
        await names_queue.put(name)
    names_len = names_queue.qsize()
    pbar = tqdm_asyncio(total=names_len, desc="Online search")
    callback(f"正在线上查询更新, 共{names_len}个频道", 0)
    # with ThreadPoolExecutor(max_workers=5) as pool:
    while not names_queue.empty():
        # loop = get_running_loop()
        name = await names_queue.get()
        process_channel_by_online_search(name)
        # loop.run_in_executor(pool, process_channel_by_online_search, name, proxy)
    driver.quit()
    pbar.close()
    return channels
