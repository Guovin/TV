from selenium import webdriver
from aiohttp_retry import RetryClient, ExponentialRetry
import asyncio
from time import time
import re
import datetime
import os
import urllib.parse
import ipaddress
from urllib.parse import urlparse
import requests
import re
from bs4 import BeautifulSoup
from bs4 import NavigableString
import fofa_map
from collections import defaultdict
from tqdm.asyncio import tqdm_asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import concurrent.futures
import sys
import importlib.util

timeout = 10
max_retries = 3


def retry_func(func, retries=max_retries + 1, name=""):
    """
    Retry the function
    """
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            count = retries - 1
            if name and i < count:
                print(f"Failed to connect to the {name}. Retrying {i+1}...")
            if i == count:
                break
            else:
                continue


def resource_path(relative_path, persistent=False):
    """
    Get the resource path
    """
    base_path = os.path.abspath(".")
    total_path = os.path.join(base_path, relative_path)
    if persistent or os.path.exists(total_path):
        return total_path
    else:
        try:
            base_path = sys._MEIPASS
            return os.path.join(base_path, relative_path)
        except Exception:
            return total_path


def load_external_config(name):
    """
    Load the external config file
    """
    config = None
    config_path = name
    config_filename = os.path.join(os.path.dirname(sys.executable), config_path)

    if os.path.exists(config_filename):
        spec = importlib.util.spec_from_file_location(name, config_filename)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
    else:
        import config

    return config


config_path = resource_path("user_config.py")
default_config_path = resource_path("config.py")
config = (
    load_external_config("user_config.py")
    if os.path.exists(config_path)
    else load_external_config("config.py")
)


def setup_driver(proxy=None):
    """
    Setup the driver for selenium
    """
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("blink-settings=imagesEnabled=false")
    options.add_argument("--log-level=3")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("blink-settings=imagesEnabled=false")
    if proxy:
        options.add_argument("--proxy-server=%s" % proxy)
    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def get_proxy_list(page_count=1):
    """
    Get the proxy list
    """
    url_pattern = [
        "https://www.kuaidaili.com/free/inha/{}/",
        "https://www.kuaidaili.com/free/intr/{}/",
    ]
    proxy_list = []
    driver = setup_driver()
    for page_index in range(1, page_count + 1):
        for pattern in url_pattern:
            url = pattern.format(page_index)
            retry_func(lambda: driver.get(url), name=url)
            source = re.sub(
                r"<!--.*?-->",
                "",
                driver.page_source,
                flags=re.DOTALL,
            )
            soup = BeautifulSoup(source, "html.parser")
            table = soup.find("table")
            trs = table.find_all("tr") if table else []
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].get_text().strip()
                port = tds[1].get_text().strip()
                proxy = f"{ip}:{port}"
                proxy_list.append(proxy)

    return proxy_list


def format_channel_name(name):
    """
    Format the channel name with sub and replace and lower
    """
    sub_pattern = (
        r"-|_|\((.*?)\)|\[(.*?)\]| |频道|标清|高清|HD|hd|超清|超高|超高清|中央|央视|台"
    )
    name = re.sub(sub_pattern, "", name)
    name = name.replace("plus", "+")
    name = name.replace("PLUS", "+")
    name = name.replace("＋", "+")
    name = name.replace("CCTV1综合", "CCTV1")
    name = name.replace("CCTV2财经", "CCTV2")
    name = name.replace("CCTV3综艺", "CCTV3")
    name = name.replace("CCTV4国际", "CCTV4")
    name = name.replace("CCTV4中文国际", "CCTV4")
    name = name.replace("CCTV4欧洲", "CCTV4")
    name = name.replace("CCTV5体育", "CCTV5")
    name = name.replace("CCTV5+体育赛视", "CCTV5+")
    name = name.replace("CCTV5+体育赛事", "CCTV5+")
    name = name.replace("CCTV5+体育", "CCTV5+")
    name = name.replace("CCTV6电影", "CCTV6")
    name = name.replace("CCTV7军事", "CCTV7")
    name = name.replace("CCTV7军农", "CCTV7")
    name = name.replace("CCTV7农业", "CCTV7")
    name = name.replace("CCTV7国防军事", "CCTV7")
    name = name.replace("CCTV8电视剧", "CCTV8")
    name = name.replace("CCTV9记录", "CCTV9")
    name = name.replace("CCTV9纪录", "CCTV9")
    name = name.replace("CCTV10科教", "CCTV10")
    name = name.replace("CCTV11戏曲", "CCTV11")
    name = name.replace("CCTV12社会与法", "CCTV12")
    name = name.replace("CCTV13新闻", "CCTV13")
    name = name.replace("CCTV新闻", "CCTV13")
    name = name.replace("CCTV14少儿", "CCTV14")
    name = name.replace("CCTV15音乐", "CCTV15")
    name = name.replace("CCTV16奥林匹克", "CCTV16")
    name = name.replace("CCTV17农业农村", "CCTV17")
    name = name.replace("CCTV17农业", "CCTV17")
    return name.lower()


def get_channel_items():
    """
    Get the channel items from the source file
    """
    # Open the source file and read all lines.
    user_source_file = (
        "user_" + config.source_file
        if os.path.exists("user_" + config.source_file)
        else getattr(config, "source_file", "demo.txt")
    )

    # Create a dictionary to store the channels.
    channels = defaultdict(lambda: defaultdict(list))
    current_category = ""
    pattern = r"^(.*?),(?!#genre#)(.*?)$"

    with open(resource_path(user_source_file), "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "#genre#" in line:
                # This is a new channel, create a new key in the dictionary.
                current_category = line.split(",")[0]
            else:
                # This is a url, add it to the list of urls for the current channel.
                match = re.search(pattern, line)
                if match is not None:
                    name = match.group(1).strip()
                    url = match.group(2).strip()
                    if url and url not in channels[current_category][name]:
                        channels[current_category][name].append(url)

    return channels


def get_pbar_remaining(pbar, start_time):
    """
    Get the remaining time of the progress bar
    """
    try:
        elapsed = time() - start_time
        completed_tasks = pbar.n
        if completed_tasks > 0:
            avg_time_per_task = elapsed / completed_tasks
            remaining_tasks = pbar.total - completed_tasks
            remaining_time = pbar.format_interval(avg_time_per_task * remaining_tasks)
        else:
            remaining_time = "未知"
        return remaining_time
    except Exception as e:
        print(f"Error: {e}")


async def get_channels_by_subscribe_urls(callback):
    """
    Get the channels by subscribe urls
    """
    channels = {}
    pattern = r"^(.*?),(?!#genre#)(.*?)$"
    subscribe_urls_len = len(config.subscribe_urls)
    pbar = tqdm_asyncio(total=subscribe_urls_len)
    start_time = time()

    def process_subscribe_channels(subscribe_url):
        try:
            response = None
            try:
                response = retry_func(
                    lambda: requests.get(subscribe_url, timeout=timeout),
                    name=subscribe_url,
                )
            except requests.exceptions.Timeout:
                print(f"Timeout on {subscribe_url}")
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
            pbar.set_description(f"Processing subscribe, {remain} urls remaining")
            callback(
                f"正在获取订阅源更新, 剩余{remain}个订阅源待获取, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / subscribe_urls_len) * 100),
            )
            if config.open_online_search and pbar.n / subscribe_urls_len == 1:
                callback("正在获取在线搜索结果, 请耐心等待", 0)

    pbar.set_description(f"Processing subscribe, {subscribe_urls_len} urls remaining")
    callback(f"正在获取订阅源更新, 共{subscribe_urls_len}个订阅源", 0)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        loop = asyncio.get_running_loop()
        tasks = []
        for subscribe_url in config.subscribe_urls:
            task = loop.run_in_executor(pool, process_subscribe_channels, subscribe_url)
            tasks.append(task)
        await tqdm_asyncio.gather(*tasks, disable=True)
    print("Finished processing subscribe urls")
    pbar.close()
    return channels


async def get_channels_by_online_search(names, callback):
    """
    Get the channels by online search
    """
    channels = {}
    pageUrl = await use_accessible_url(callback)
    if not pageUrl:
        return channels
    github_actions = os.environ.get("GITHUB_ACTIONS")
    if github_actions:
        proxy_list = get_proxy_list()
        response_times = await asyncio.gather(*(get_speed(url) for url in proxy_list))
        proxy_list_with_speed = [
            (proxy, response_time)
            for proxy, response_time in zip(proxy_list, response_times)
            if response_time is not None
        ]
        proxy_list_with_speed.sort(key=lambda x: x[1])
        best_proxy = proxy_list_with_speed[0][0] if proxy_list_with_speed else None
        print(f"Using proxy: {best_proxy}")
    start_time = time()

    def process_channel_by_online_search(name):
        driver = setup_driver(best_proxy if github_actions else None)
        wait = WebDriverWait(driver, timeout)
        info_list = []
        try:
            retry_func(lambda: driver.get(pageUrl), name=f"online search:{name}")
            search_box = retry_func(
                lambda: wait.until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
                )
            )
            search_box.clear()
            search_box.send_keys(name)
            submit_button = retry_func(
                lambda: wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))
                )
            )
            driver.execute_script("arguments[0].click();", submit_button)
            isFavorite = name in config.favorite_list
            pageNum = (
                config.favorite_page_num if isFavorite else config.default_page_num
            )
            for page in range(1, pageNum + 1):
                try:
                    if page > 1:
                        page_link = retry_func(
                            lambda: wait.until(
                                EC.element_to_be_clickable(
                                    (
                                        By.XPATH,
                                        f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
                                    )
                                )
                            )
                        )
                        driver.execute_script("arguments[0].click();", page_link)
                    source = re.sub(
                        r"<!--.*?-->",
                        "",
                        driver.page_source,
                        flags=re.DOTALL,
                    )
                    soup = BeautifulSoup(source, "html.parser")
                    if soup:
                        results = get_results_from_soup(soup, name)
                        print(name, "page:", page, "results len:", len(results))
                        for result in results:
                            url, date, resolution = result
                            if url and check_url_by_patterns(url):
                                info_list.append((url, date, resolution))
                    else:
                        print(f"No results found for {name}")
                except Exception as e:
                    print(f"Error on page {page}: {e}")
                    continue
        except Exception as e:
            print(f"Error on search: {e}")
            pass
        finally:
            channels[format_channel_name(name)] = info_list
            names_queue.task_done()
            pbar.update()
            pbar.set_description(
                f"Processing online search, {names_len - pbar.n} channels remaining"
            )
            callback(
                f"正在线上查询更新, 剩余{names_len - pbar.n}个频道待查询, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / names_len) * 100),
            )
            driver.quit()

    names_queue = asyncio.Queue()
    for name in names:
        await names_queue.put(name)
    names_len = names_queue.qsize()
    pbar = tqdm_asyncio(total=names_len)
    pbar.set_description(f"Processing online search, {names_len} channels remaining")
    callback(f"正在线上查询更新, 共{names_len}个频道", 0)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        while not names_queue.empty():
            loop = asyncio.get_running_loop()
            name = await names_queue.get()
            loop.run_in_executor(pool, process_channel_by_online_search, name)
    print("Finished processing online search")
    pbar.close()
    return channels


def update_channel_urls_txt(cate, name, urls):
    """
    Update the category and channel urls to the final file
    """
    genre_line = cate + ",#genre#\n"
    filename = "result_new.txt"

    if not os.path.exists(filename):
        open(filename, "w").close()

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    with open(filename, "a", encoding="utf-8") as f:
        if genre_line not in content:
            f.write(genre_line)
        for url in urls:
            if url is not None:
                f.write(name + "," + url + "\n")


def update_file(final_file, old_file):
    """
    Update the file
    """
    old_file_path = resource_path(old_file, persistent=True)
    final_file_path = resource_path(final_file, persistent=True)
    if os.path.exists(old_file_path):
        os.replace(old_file_path, final_file_path)


def get_channel_url(element):
    """
    Get the url, date and resolution
    """
    url = None
    urlRegex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    url_search = re.search(
        urlRegex,
        element.get_text(strip=True),
    )
    if url_search:
        url = url_search.group()
    return url


def get_channel_info(element):
    """
    Get the channel info
    """
    date, resolution = None, None
    info_text = element.get_text(strip=True)
    if info_text:
        date, resolution = (
            (info_text.partition(" ")[0] if info_text.partition(" ")[0] else None),
            (
                info_text.partition(" ")[2].partition("•")[2]
                if info_text.partition(" ")[2].partition("•")[2]
                else None
            ),
        )
    return date, resolution


def get_results_from_soup(soup, name):
    """
    Get the results from the soup
    """
    results = []
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            url = get_channel_url(element)
            if url and not any(item[0] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if url_element:
                    name_element = url_element.find_previous_sibling()
                    if name_element:
                        channel_name = name_element.get_text(strip=True)
                        if format_channel_name(name) == format_channel_name(
                            channel_name
                        ):
                            info_element = url_element.find_next_sibling()
                            date, resolution = get_channel_info(info_element)
                            results.append((url, date, resolution))
    return results


async def get_speed(url, urlTimeout=timeout):
    """
    Get the speed of the url
    """
    retry_options = ExponentialRetry(attempts=1, max_timeout=urlTimeout)
    retry_client = RetryClient(raise_for_status=False, retry_options=retry_options)
    start = time()
    total = float("inf")
    try:
        async with retry_client.get(url) as response:
            resStatus = response.status
            end = time()
            if resStatus == 200:
                total = int(round((end - start) * 1000))
            else:
                total = float("inf")
    except:
        total = float("inf")
    await retry_client.close()
    return total


async def sort_urls_by_speed_and_resolution(infoList):
    """
    Sort by speed and resolution
    """
    response_times = await asyncio.gather(*(get_speed(url) for url, _, _ in infoList))
    valid_responses = [
        (info, rt) for info, rt in zip(infoList, response_times) if rt != float("inf")
    ]

    def extract_resolution(resolution_str):
        numbers = re.findall(r"\d+x\d+", resolution_str)
        if numbers:
            width, height = map(int, numbers[0].split("x"))
            return width * height
        else:
            return 0

    default_response_time_weight = 0.5
    default_resolution_weight = 0.5
    response_time_weight = getattr(
        config, "response_time_weight", default_response_time_weight
    )
    resolution_weight = getattr(config, "resolution_weight", default_resolution_weight)
    # Check if weights are valid
    if not (
        0 <= response_time_weight <= 1
        and 0 <= resolution_weight <= 1
        and response_time_weight + resolution_weight == 1
    ):
        response_time_weight = default_response_time_weight
        resolution_weight = default_resolution_weight

    def combined_key(item):
        (_, _, resolution), response_time = item
        resolution_value = extract_resolution(resolution) if resolution else 0
        return (
            -(response_time_weight * response_time)
            + resolution_weight * resolution_value
        )

    sorted_res = sorted(valid_responses, key=combined_key, reverse=True)
    return sorted_res


def filter_by_date(data):
    """
    Filter by date and limit
    """
    default_recent_days = 30
    use_recent_days = getattr(config, "recent_days", 30)
    if not isinstance(use_recent_days, int) or use_recent_days <= 0:
        use_recent_days = default_recent_days
    start_date = datetime.datetime.now() - datetime.timedelta(days=use_recent_days)
    recent_data = []
    unrecent_data = []
    for (url, date, resolution), response_time in data:
        item = ((url, date, resolution), response_time)
        if date:
            date = datetime.datetime.strptime(date, "%m-%d-%Y")
            if date >= start_date:
                recent_data.append(item)
            else:
                unrecent_data.append(item)
        else:
            unrecent_data.append(item)
    recent_data_len = len(recent_data)
    if recent_data_len == 0:
        recent_data = unrecent_data
    elif recent_data_len < config.urls_limit:
        recent_data.extend(unrecent_data[: config.urls_limit - len(recent_data)])
    return recent_data


def get_total_urls_from_info_list(infoList):
    """
    Get the total urls from info list
    """
    total_urls = [url for url, _, _ in infoList]
    return list(dict.fromkeys(total_urls))[: int(config.urls_limit)]


def get_total_urls_from_sorted_data(data):
    """
    Get the total urls with filter by date and depulicate from sorted data
    """
    total_urls = []
    if len(data) > config.urls_limit:
        total_urls = [url for (url, _, _), _ in filter_by_date(data)]
    else:
        total_urls = [url for (url, _, _), _ in data]
    return list(dict.fromkeys(total_urls))[: config.urls_limit]


def is_ipv6(url):
    """
    Check if the url is ipv6
    """
    try:
        host = urllib.parse.urlparse(url).hostname
        ipaddress.IPv6Address(host)
        return True
    except ValueError:
        return False


def check_url_ipv_type(url):
    """
    Check if the url is compatible with the ipv type in the config
    """
    ipv_type = getattr(config, "ipv_type", "ipv4")
    if ipv_type == "ipv4":
        return not is_ipv6(url)
    elif ipv_type == "ipv6":
        return is_ipv6(url)
    else:
        return True


def check_by_domain_blacklist(url):
    """
    Check by domain blacklist
    """
    domain_blacklist = [
        urlparse(domain).netloc if urlparse(domain).scheme else domain
        for domain in getattr(config, "domain_blacklist", [])
    ]
    return urlparse(url).netloc not in domain_blacklist


def check_by_url_keywords_blacklist(url):
    """
    Check by URL blacklist keywords
    """
    url_keywords_blacklist = getattr(config, "url_keywords_blacklist", [])
    return not any(keyword in url for keyword in url_keywords_blacklist)


def check_url_by_patterns(url):
    """
    Check the url by patterns
    """
    return (
        check_url_ipv_type(url)
        and check_by_domain_blacklist(url)
        and check_by_url_keywords_blacklist(url)
    )


def filter_urls_by_patterns(urls):
    """
    Filter urls by patterns
    """
    urls = [url for url in urls if check_url_ipv_type(url)]
    urls = [url for url in urls if check_by_domain_blacklist(url)]
    urls = [url for url in urls if check_by_url_keywords_blacklist(url)]
    return urls


async def use_accessible_url(callback):
    """
    Check if the url is accessible
    """
    callback(f"正在获取最优的在线检索节点", 0)
    baseUrl1 = "https://www.foodieguide.com/iptvsearch/"
    baseUrl2 = "http://tonkiang.us/"
    task1 = asyncio.create_task(get_speed(baseUrl1, 30))
    task2 = asyncio.create_task(get_speed(baseUrl2, 30))
    task_results = await asyncio.gather(task1, task2)
    callback(f"获取在线检索节点完成", 100)
    if task_results[0] == float("inf") and task_results[1] == float("inf"):
        return None
    if task_results[0] < task_results[1]:
        return baseUrl1
    else:
        return baseUrl2


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
    pbar = tqdm_asyncio(total=fofa_urls_len)
    start_time = time()
    fofa_results = {}

    def process_fofa_channels(fofa_url, pbar, fofa_urls_len, callback):
        driver = setup_driver()
        try:
            retry_func(lambda: driver.get(fofa_url), name=fofa_url)
            fofa_source = re.sub(r"<!--.*?-->", "", driver.page_source, flags=re.DOTALL)
            urls = set(re.findall(r"https?://[\w\.-]+:\d+", fofa_source))
            channels = {}
            for url in urls:
                try:
                    final_url = url + "/iptv/live/1000.json?key=txiptv"
                    response = retry_func(
                        lambda: requests.get(final_url, timeout=timeout),
                        name=final_url,
                    )
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
            # print(e)
            pass
        finally:
            pbar.update()
            remain = fofa_urls_len - pbar.n
            pbar.set_description(f"Processing multicast, {remain} regions remaining")
            callback(
                f"正在获取组播源更新, 剩余{remain}个地区待获取, 预计剩余时间: {get_pbar_remaining(pbar, start_time)}",
                int((pbar.n / fofa_urls_len) * 100),
            )
            if config.open_online_search and pbar.n / fofa_urls_len == 1:
                callback("正在获取在线搜索结果, 请耐心等待", 0)
            driver.quit()

    pbar.set_description(f"Processing multicast, {fofa_urls_len} regions remaining")
    callback(f"正在获取组播源更新, 共{fofa_urls_len}个地区", 0)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        loop = asyncio.get_running_loop()
        tasks = []
        for fofa_url in fofa_urls:
            task = loop.run_in_executor(
                pool, process_fofa_channels, fofa_url, pbar, fofa_urls_len, callback
            )
            tasks.append(task)
        await tqdm_asyncio.gather(*tasks, disable=True)
    pbar.close()
    return fofa_results


def merge_objects(*objects):
    """
    Merge objects
    """
    merged_dict = {}
    for obj in objects:
        if not isinstance(obj, dict):
            raise TypeError("All input objects must be dictionaries")
        for key, value in obj.items():
            if key not in merged_dict:
                merged_dict[key] = set()
            if isinstance(value, set):
                merged_dict[key].update(value)
            elif isinstance(value, list):
                for item in value:
                    merged_dict[key].add(item)
            else:
                merged_dict[key].add(value)
    for key, value in merged_dict.items():
        merged_dict[key] = list(value)
    return merged_dict
