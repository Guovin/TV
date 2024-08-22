from asyncio import create_task, gather
from utils.speed import get_speed
from utils.channel import (
    get_results_from_multicast_soup,
    get_results_from_multicast_soup_requests,
    format_channel_name,
)
from utils.tools import get_pbar_remaining, get_soup
from utils.config import config
from updates.proxy import get_proxy, get_proxy_next
from time import time, sleep
from driver.setup import setup_driver
from utils.retry import (
    retry_func,
    locate_element_with_retry,
    find_clickable_element_with_retry,
)
from selenium.webdriver.common.by import By
from tqdm.asyncio import tqdm_asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_custom.utils import get_soup_requests, close_session
import urllib.parse as urlparse
from urllib.parse import parse_qs
from updates.subscribe import get_channels_by_subscribe_urls
from collections import defaultdict


async def use_accessible_url(callback):
    """
    Check if the url is accessible
    """
    callback(f"正在获取最优的酒店源检索节点", 0)
    baseUrl1 = "https://www.foodieguide.com/iptvsearch/hoteliptv.php"
    baseUrl2 = "http://tonkiang.us/hoteliptv.php"
    task1 = create_task(get_speed(baseUrl1, timeout=30))
    task2 = create_task(get_speed(baseUrl2, timeout=30))
    task_results = await gather(task1, task2)
    callback(f"获取酒店源检索节点完成", 100)
    if task_results[0] == float("inf") and task_results[1] == float("inf"):
        return None
    if task_results[0] < task_results[1]:
        return baseUrl1
    else:
        return baseUrl2


def search_submit(driver, name):
    """
    Input key word and submit with driver
    """
    search_box = locate_element_with_retry(driver, (By.XPATH, '//input[@type="text"]'))
    if not search_box:
        return
    search_box.clear()
    search_box.send_keys(name)
    submit_button = find_clickable_element_with_retry(
        driver, (By.XPATH, '//input[@type="submit"]')
    )
    if not submit_button:
        return
    sleep(1)
    driver.execute_script("arguments[0].click();", submit_button)


async def get_channels_by_hotel(names, callback):
    """
    Get the channels by multicase
    """
    channels = {}
    # pageUrl = await use_accessible_url(callback)
    pageUrl = "http://tonkiang.us/hoteliptv.php"
    # if not pageUrl:
    #     return channels
    proxy = None
    open_proxy = config.getboolean("Settings", "open_proxy")
    open_driver = config.getboolean("Settings", "open_driver")
    page_num = config.getint("Settings", "hotel_page_num")
    region_list = config.get("Settings", "hotel_region_list").split(",")
    if open_proxy:
        proxy = await get_proxy(pageUrl, best=True, with_test=True)
    start_time = time()

    def process_region_by_hotel(region):
        nonlocal proxy, open_driver, page_num
        name = f"{region}"
        info_list = []
        try:
            if open_driver:
                driver = setup_driver(proxy)
                try:
                    retry_func(lambda: driver.get(pageUrl), name=f"hotel search:{name}")
                except Exception as e:
                    if open_proxy:
                        proxy = get_proxy_next()
                    driver.close()
                    driver.quit()
                    driver = setup_driver(proxy)
                    driver.get(pageUrl)
                search_submit(driver, name)
            else:
                page_soup = None
                post_form = {"saerch": name}
                code = None
                try:
                    page_soup = retry_func(
                        lambda: get_soup_requests(pageUrl, data=post_form, proxy=proxy),
                        name=f"hotel search:{name}",
                    )
                except Exception as e:
                    if open_proxy:
                        proxy = get_proxy_next()
                    page_soup = get_soup_requests(pageUrl, data=post_form, proxy=proxy)
                if not page_soup:
                    print(f"{name}:Request fail.")
                    return {"region": region, "type": type, "data": info_list}
                else:
                    a_tags = page_soup.find_all("a", href=True)
                    for a_tag in a_tags:
                        href_value = a_tag["href"]
                        parsed_url = urlparse.urlparse(href_value)
                        code = parse_qs(parsed_url.query).get("code", [None])[0]
                        if code:
                            break
            # retry_limit = 3
            for page in range(1, page_num + 1):
                # retries = 0
                # if not open_driver and page == 1:
                #     retries = 2
                # while retries < retry_limit:
                try:
                    if page > 1:
                        if open_driver:
                            page_link = find_clickable_element_with_retry(
                                driver,
                                (
                                    By.XPATH,
                                    f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                ),
                            )
                            if not page_link:
                                # break
                                continue
                            sleep(1)
                            driver.execute_script("arguments[0].click();", page_link)
                        else:
                            request_url = (
                                f"{pageUrl}?net={name}&page={page}&code={code}"
                            )
                            page_soup = retry_func(
                                lambda: get_soup_requests(request_url, proxy=proxy),
                                name=f"hotel search:{name}, page:{page}",
                            )
                    sleep(1)
                    soup = get_soup(driver.page_source) if open_driver else page_soup
                    if soup:
                        results = (
                            get_results_from_multicast_soup(soup, hotel=True)
                            if open_driver
                            else get_results_from_multicast_soup_requests(
                                soup, hotel=True
                            )
                        )
                        print(name, "page:", page, "results num:", len(results))
                        if len(results) == 0:
                            print(f"{name}:No results found")
                            # if open_driver:
                            #     driver.refresh()
                            # retries += 1
                            # continue
                        # elif len(results) <= 3:
                        #     if open_driver:
                        #         next_page_link = find_clickable_element_with_retry(
                        #             driver,
                        #             (
                        #                 By.XPATH,
                        #                 f'//a[contains(@href, "={page+1}") and contains(@href, "{name}")]',
                        #             ),
                        #             retries=1,
                        #         )
                        #         if next_page_link:
                        #             if open_proxy:
                        #                 proxy = get_proxy_next()
                        #             driver.close()
                        #             driver.quit()
                        #             driver = setup_driver(proxy)
                        #             search_submit(driver, name)
                        #     retries += 1
                        #     continue
                        info_list = info_list + results
                        # break
                    else:
                        print(f"{name}:No results found")
                        # if open_driver:
                        #     driver.refresh()
                        # retries += 1
                        # continue
                except Exception as e:
                    print(f"{name}:Error on page {page}: {e}")
                    # break
                    continue
            # if retries == retry_limit:
            #     print(f"{name}:Reached retry limit, moving to next page")
        except Exception as e:
            print(f"{name}:Error on search: {e}")
            pass
        finally:
            if open_driver:
                driver.close()
                driver.quit()
            pbar.update()
            callback(
                f"正在进行酒店源更新, 剩余{region_list_len - pbar.n}个地区待查询, 预计剩余时间: {get_pbar_remaining(n=pbar.n, total=pbar.total, start_time=start_time)}",
                int((pbar.n / region_list_len) * 100),
            )
            return {"region": region, "type": type, "data": info_list}

    region_list_len = len(region_list)
    pbar = tqdm_asyncio(total=region_list_len, desc="Hotel search")
    callback(f"正在进行酒店源更新, 共{region_list_len}个地区", 0)
    search_region_result = defaultdict(list)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(process_region_by_hotel, region): region
            for region in region_list
        }

        for future in as_completed(futures):
            region = futures[future]
            result = future.result()
            data = result.get("data")

            if data:
                for item in data:
                    url = item.get("url")
                    date = item.get("date")
                    if url:
                        search_region_result[region].append((url, date, None))
    urls = [
        f"http://{url}/ZHGXTV/Public/json/live_interface.txt"
        for result in search_region_result.values()
        for url, _, _ in result
    ]
    region_urls_data = await get_channels_by_subscribe_urls(urls, retry=False)
    for name in names:
        channels[name] = region_urls_data.get(format_channel_name(name), [])
    if not open_driver:
        close_session()
    pbar.close()
    return channels
