from asyncio import create_task, gather
from utils.speed import get_speed
from utils.channel import (
    get_results_from_multicast_soup,
    get_results_from_multicast_soup_requests,
    get_channel_multicast_name_region_type_result,
    get_channel_multicast_region_type_list,
    get_channel_multicast_result,
)
from utils.tools import get_pbar_remaining, get_soup
from utils.config import get_config
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
from driver.utils import get_soup_driver
import json
from collections import defaultdict

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


def get_region_urls_from_IPTV_Multicast_source():
    """
    Get the region urls from IPTV_Multicast_source
    """
    region_url = {}
    origin_url = "https://github.com/xisohi/IPTV-Multicast-source/blob/main/README.md"
    soup = get_soup_driver(origin_url)
    tbody = soup.find("tbody")
    trs = tbody.find_all("tr") if tbody else []
    for tr in trs:
        tds = tr.find_all("td")
        name = tds[0].get_text().strip()
        unicom = tds[1].find("a", href=True).get("href")
        mobile = tds[2].find("a", href=True).get("href")
        telecom = tds[3].find("a", href=True).get("href")
        if name not in region_url:
            region_url[name] = {}
        region_url[name]["联通"] = unicom
        region_url[name]["移动"] = mobile
        region_url[name]["电信"] = telecom
    with open("updates/multicast/multicast_map.json", "w", encoding="utf-8") as f:
        json.dump(region_url, f, ensure_ascii=False, indent=4)


def get_multicast_urls_info_from_region_list():
    """
    Get the multicast urls info from region
    """
    region_list = config.get("Settings", "region_list").split(",")
    urls_info = []
    with open("updates/multicast/multicast_map.json", "r", encoding="utf-8") as f:
        region_url = json.load(f)
    if "all" in region_list:
        urls_info = [
            {"region": region, "type": type, "url": url}
            for region, value in region_url.items()
            for type, url in value.items()
        ]
    else:
        for region in region_list:
            if region in region_url:
                region_data = [
                    {"region": region, "type": type, "url": url}
                    for type, url in region_url[region].items()
                ]
                urls_info.append(region_data)
    return urls_info


async def get_multicast_region_result():
    """
    Get multicast region result
    """
    multicast_region_urls_info = get_multicast_urls_info_from_region_list()
    multicast_result = await get_channels_by_subscribe_urls(
        urls=multicast_region_urls_info, multicast=True
    )
    with open(
        "updates/multicast/multicast_region_result.json", "w", encoding="utf-8"
    ) as f:
        json.dump(multicast_result, f, ensure_ascii=False, indent=4)


async def get_channels_by_multicast(names, callback):
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
    default_page_num = config.getint("Settings", "default_page_num")
    if open_proxy:
        proxy = await get_proxy(pageUrl, best=True, with_test=True)
    start_time = time()
    with open(
        "updates/multicast/multicast_region_result.json", "r", encoding="utf-8"
    ) as f:
        multicast_region_result = json.load(f)
    name_region_type_result = get_channel_multicast_name_region_type_result(
        multicast_region_result, names
    )
    region_type_list = get_channel_multicast_region_type_list(name_region_type_result)

    def process_channel_by_multicast(region, type):
        nonlocal proxy, open_driver, default_page_num
        name = f"{region}{type}"
        info_list = []
        try:
            if open_driver:
                driver = setup_driver(proxy)
                try:
                    retry_func(
                        lambda: driver.get(pageUrl), name=f"multicast search:{name}"
                    )
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
                        name=f"multicast search:{name}",
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
            pageNum = default_page_num
            # retry_limit = 3
            for page in range(1, pageNum + 1):
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
                                name=f"multicast search:{name}, page:{page}",
                            )
                    sleep(1)
                    soup = get_soup(driver.page_source) if open_driver else page_soup
                    if soup:
                        results = (
                            get_results_from_multicast_soup(soup)
                            if open_driver
                            else get_results_from_multicast_soup_requests(soup)
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
                f"正在进行组播更新, 剩余{region_type_list_len - pbar.n}个地区组播源待查询, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / region_type_list_len) * 100),
            )
            return {"region": region, "type": type, "data": info_list}

    region_type_list_len = len(region_type_list)
    pbar = tqdm_asyncio(total=region_type_list_len, desc="Multicast search")
    callback(
        f"正在进行组播更新, {len(names)}个频道, 共{region_type_list_len}个地区组播源", 0
    )
    search_region_type_result = defaultdict(lambda: defaultdict(list))
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(process_channel_by_multicast, region, type): (region, type)
            for region, type in region_type_list
        }

        for future in as_completed(futures):
            region, type = futures[future]
            result = future.result()
            data = result.get("data")

            if data:
                region_type_results = search_region_type_result[region][type]
                for item in data:
                    url = item.get("url")
                    date = item.get("date")
                    if url:
                        region_type_results.append((url, date, None))
    channels = get_channel_multicast_result(
        name_region_type_result, search_region_type_result
    )
    if not open_driver:
        close_session()
    pbar.close()
    return channels
