from asyncio import create_task, gather
from utils.speed import get_speed
from utils.channel import (
    format_channel_name,
    get_results_from_multicast_soup,
    get_results_from_multicast_soup_requests,
)
from utils.tools import (
    check_url_by_patterns,
    get_pbar_remaining,
    get_soup,
    get_total_urls_from_info_list,
)
from utils.config import get_config
from proxy import get_proxy, get_proxy_next
from time import time, sleep
from driver.setup import setup_driver
from utils.retry import (
    retry_func,
    locate_element_with_retry,
    find_clickable_element_with_retry,
)
from selenium.webdriver.common.by import By
from tqdm.asyncio import tqdm_asyncio
from concurrent.futures import ThreadPoolExecutor
from requests_custom.utils import get_soup_requests, close_session
import urllib.parse as urlparse
from urllib.parse import parse_qs
import multicast_map
from subscribe import get_channels_by_subscribe_urls
import re

config = get_config()


async def use_accessible_url(callback):
    """
    Check if the url is accessible
    """
    callback(f"正在获取最优的组播源检索节点", 0)
    baseUrl1 = "https://www.foodieguide.com/iptvsearch/hoteliptv.php"
    baseUrl2 = "http://tonkiang.us/hoteliptv.php"
    task1 = create_task(get_speed(baseUrl1, timeout=30))
    task2 = create_task(get_speed(baseUrl2, timeout=30))
    task_results = await gather(task1, task2)
    callback(f"获取组播源检索节点完成", 100)
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


def get_multicast_urls_from_region_list():
    """
    Get the multicast url from region
    """
    region_list = getattr(config, "region_list", [])
    urls = []
    region_url = getattr(multicast_map, "region_url")
    if "all" in region_list:
        urls = [url for url in region_url.values() if url]
    else:
        for region in region_list:
            if region in region_url:
                urls.append(region_url[region])
    return urls


def get_multicast_ip_list(urls):
    """
    Get multicast ip from url
    """
    ip_list = []
    for url in urls:
        pattern = r"rtp://((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?)"
        matcher = re.search(pattern, url)
        if matcher:
            ip_list.append(matcher.group(1))
    return ip_list


async def get_channels_by_multicast(names, callback):
    """
    Get the channels by multicase
    """
    multicast_region_urls = get_multicast_urls_from_region_list()
    multicast_results = await get_channels_by_subscribe_urls(
        urls=multicast_region_urls, callback=callback
    )
    channels = {}
    # pageUrl = await use_accessible_url(callback)
    pageUrl = "http://tonkiang.us/hoteliptv.php"
    # if not pageUrl:
    #     return channels
    if not multicast_results:
        return channels
    proxy = None
    if config.open_proxy:
        proxy = await get_proxy(pageUrl, best=True, with_test=True)
    start_time = time()

    def process_channel_by_multicast(name):
        format_name = format_channel_name(name)
        info_list = []
        multicast_info_list = multicast_results.get(format_name)
        if not multicast_info_list:
            return {"name": format_name, "data": info_list}
        multicast_urls = get_total_urls_from_info_list(multicast_info_list)
        multicast_ip_list = get_multicast_ip_list(multicast_urls)
        if not multicast_ip_list:
            return {"name": format_name, "data": info_list}
        nonlocal proxy
        try:
            if config.open_driver:
                driver = setup_driver(proxy)
                try:
                    retry_func(
                        lambda: driver.get(pageUrl), name=f"multicast search:{name}"
                    )
                except Exception as e:
                    if config.open_proxy:
                        proxy = get_proxy_next()
                    driver.close()
                    driver.quit()
                    driver = setup_driver(proxy)
                    driver.get(pageUrl)
                search_submit(driver, name)
            else:
                page_soup = None
                request_url = f"{pageUrl}?net={name}"
                code = None
                try:
                    page_soup = retry_func(
                        lambda: get_soup_requests(request_url, proxy=proxy),
                        name=f"multicast search:{name}",
                    )
                except Exception as e:
                    if config.open_proxy:
                        proxy = get_proxy_next()
                    page_soup = get_soup_requests(request_url, proxy=proxy)
                if not page_soup:
                    print(f"{name}:Request fail.")
                    return {"name": format_name, "data": info_list}
                else:
                    a_tags = page_soup.find_all("a", href=True)
                    for a_tag in a_tags:
                        href_value = a_tag["href"]
                        parsed_url = urlparse.urlparse(href_value)
                        code = parse_qs(parsed_url.query).get("code", [None])[0]
                        if code:
                            break
            isFavorite = name in config.favorite_list
            pageNum = (
                config.favorite_page_num if isFavorite else config.default_page_num
            )
            retry_limit = 3
            for page in range(1, pageNum + 1):
                retries = 0
                if not config.open_driver and page == 1:
                    retries = 2
                while retries < retry_limit:
                    try:
                        if page > 1:
                            if config.open_driver:
                                page_link = find_clickable_element_with_retry(
                                    driver,
                                    (
                                        By.XPATH,
                                        f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                    ),
                                )
                                if not page_link:
                                    break
                                sleep(1)
                                driver.execute_script(
                                    "arguments[0].click();", page_link
                                )
                            else:
                                request_url = (
                                    f"{pageUrl}?net={name}&page={page}&code={code}"
                                )
                                page_soup = retry_func(
                                    lambda: get_soup_requests(request_url, proxy=proxy),
                                    name=f"multicast search:{name}, page:{page}",
                                )
                        sleep(1)
                        soup = (
                            get_soup(driver.page_source)
                            if config.open_driver
                            else page_soup
                        )
                        if soup:
                            results = (
                                get_results_from_multicast_soup(soup)
                                if config.open_driver
                                else get_results_from_multicast_soup_requests(soup)
                            )
                            print(name, "page:", page, "results num:", len(results))
                            if len(results) == 0:
                                print(
                                    f"{name}:No results found, refreshing page and retrying..."
                                )
                                if config.open_driver:
                                    driver.refresh()
                                retries += 1
                                continue
                            elif len(results) <= 3:
                                if config.open_driver:
                                    next_page_link = find_clickable_element_with_retry(
                                        driver,
                                        (
                                            By.XPATH,
                                            f'//a[contains(@href, "={page+1}") and contains(@href, "{name}")]',
                                        ),
                                        retries=1,
                                    )
                                    if next_page_link:
                                        if config.open_proxy:
                                            proxy = get_proxy_next()
                                        driver.close()
                                        driver.quit()
                                        driver = setup_driver(proxy)
                                        search_submit(driver, name)
                                retries += 1
                                continue
                            for result in results:
                                url, date, resolution = result
                                if url and check_url_by_patterns(url):
                                    for ip in multicast_ip_list:
                                        total_url = f"http://{url}/rtp/{ip}"
                                        info_list.append((total_url, date, resolution))
                            break
                        else:
                            print(
                                f"{name}:No results found, refreshing page and retrying..."
                            )
                            if config.open_driver:
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
            if config.open_driver:
                driver.close()
                driver.quit()
            pbar.update()
            callback(
                f"正在进行组播更新, 剩余{names_len - pbar.n}个频道待查询, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / names_len) * 100),
            )
            return {"name": format_name, "data": info_list}

    names_len = len(names)
    pbar = tqdm_asyncio(total=names_len, desc="Multicast search")
    callback(f"正在进行组播更新, 共{names_len}个频道", 0)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_channel_by_multicast, name) for name in names
        ]
        for future in futures:
            result = future.result()
            name = result.get("name")
            data = result.get("data", [])
            if name:
                channels[name] = data
    if not config.open_driver:
        close_session()
    pbar.close()
    return channels
