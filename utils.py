try:
    import user_config as config
except ImportError:
    import config
import aiohttp
import asyncio
import time
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
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def formatChannelName(name):
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


def getChannelItems():
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

    with open(user_source_file, "r", encoding="utf-8") as f:
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


async def getChannelsBySubscribeUrls(channel_names):
    """
    Get the channels by subscribe urls
    """
    channels = {}
    pattern = r"^(.*?),(?!#genre#)(.*?)$"
    subscribe_urls_len = len(config.subscribe_urls)
    pbar = tqdm(total=subscribe_urls_len)
    for base_url in config.subscribe_urls:
        try:
            pbar.set_description(
                f"Processing subscribe {base_url}, {subscribe_urls_len - pbar.n} urls remaining"
            )
            try:
                response = requests.get(base_url, timeout=30)
            except requests.exceptions.Timeout:
                print(f"Timeout on {base_url}")
                continue
            content = response.text
            if content:
                lines = content.split("\n")
                for line in lines:
                    if re.match(pattern, line) is not None:
                        key = re.match(pattern, line).group(1)
                        resolution_match = re.search(r"_(\((.*?)\))", key)
                        resolution = (
                            resolution_match.group(2)
                            if resolution_match is not None
                            else None
                        )
                        key = formatChannelName(key)
                        url = re.match(pattern, line).group(2)
                        value = (url, None, resolution)
                        if key in channels:
                            if value not in channels[key]:
                                channels[key].append(value)
                        else:
                            channels[key] = [value]
        except Exception as e:
            print(f"Error on {base_url}: {e}")
            continue
        finally:
            pbar.update()
    print("Finished processing subscribe urls")
    pbar.close()
    return channels


def getChannelsInfoListByOnlineSearch(driver, pageUrl, name):
    """
    Get the channels info list by online search
    """
    wait = WebDriverWait(driver, 10)
    driver.get(pageUrl)
    search_box = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
    )
    search_box.clear()
    search_box.send_keys(name)
    submit_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]'))
    )
    driver.execute_script("arguments[0].click();", submit_button)
    isFavorite = name in config.favorite_list
    pageNum = config.favorite_page_num if isFavorite else config.default_page_num
    info_list = []
    for page in range(1, pageNum + 1):
        try:
            if page > 1:
                page_link = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f'//a[contains(@href, "={page}") and contains(@href, "{name}")]',
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
                results = getResultsFromSoup(soup, name)
                for result in results:
                    url, date, resolution = result
                    if url and checkUrlByPatterns(url):
                        info_list.append((url, date, resolution))
        except Exception as e:
            # print(f"Error on page {page}: {e}")
            continue
    return info_list


def updateChannelUrlsTxt(cate, channelUrls):
    """
    Update the category and channel urls to the final file
    """
    try:
        with open("result_new.txt", "a", encoding="utf-8") as f:
            f.write(cate + ",#genre#\n")
            for name, urls in channelUrls.items():
                for url in urls:
                    if url is not None:
                        f.write(name + "," + url + "\n")
            f.write("\n")
    finally:
        f.close


def updateFile(final_file, old_file):
    """
    Update the file
    """
    if os.path.exists(old_file):
        os.replace(old_file, final_file)


def getChannelUrl(element):
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


def getChannelInfo(element):
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


def getResultsFromSoup(soup, name):
    """
    Get the results from the soup
    """
    results = []
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            url = getChannelUrl(element)
            if url and not any(item[0] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if url_element:
                    name_element = url_element.find_previous_sibling()
                    if name_element:
                        channel_name = name_element.get_text(strip=True)
                        if name == formatChannelName(channel_name):
                            info_element = url_element.find_next_sibling()
                            date, resolution = getChannelInfo(info_element)
                            results.append((url, date, resolution))
    return results


async def getSpeed(url, urlTimeout=5):
    """
    Get the speed of the url
    """
    async with aiohttp.ClientSession() as session:
        start = time.time()
        try:
            async with session.get(url, timeout=urlTimeout) as response:
                resStatus = response.status
        except:
            return float("inf")
        end = time.time()
        if resStatus == 200:
            return int(round((end - start) * 1000))
        else:
            return float("inf")


async def sortUrlsBySpeedAndResolution(infoList):
    """
    Sort by speed and resolution
    """
    response_times = await asyncio.gather(*(getSpeed(url) for url, _, _ in infoList))
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


def filterByDate(data):
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


def getTotalUrlsFromInfoList(infoList):
    """
    Get the total urls from info list
    """
    total_urls = [url for url, _, _ in infoList]
    return list(dict.fromkeys(total_urls))[: config.urls_limit]


def getTotalUrlsFromSortedData(data):
    """
    Get the total urls with filter by date and depulicate from sorted data
    """
    total_urls = []
    if len(data) > config.urls_limit:
        total_urls = [url for (url, _, _), _ in filterByDate(data)]
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


def checkUrlIPVType(url):
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


def checkByDomainBlacklist(url):
    """
    Check by domain blacklist
    """
    domain_blacklist = [
        urlparse(domain).netloc if urlparse(domain).scheme else domain
        for domain in getattr(config, "domain_blacklist", [])
    ]
    return urlparse(url).netloc not in domain_blacklist


def checkByURLKeywordsBlacklist(url):
    """
    Check by URL blacklist keywords
    """
    url_keywords_blacklist = getattr(config, "url_keywords_blacklist", [])
    return not any(keyword in url for keyword in url_keywords_blacklist)


def checkUrlByPatterns(url):
    """
    Check the url by patterns
    """
    return (
        checkUrlIPVType(url)
        and checkByDomainBlacklist(url)
        and checkByURLKeywordsBlacklist(url)
    )


def filterUrlsByPatterns(urls):
    """
    Filter urls by patterns
    """
    urls = [url for url in urls if checkUrlIPVType(url)]
    urls = [url for url in urls if checkByDomainBlacklist(url)]
    urls = [url for url in urls if checkByURLKeywordsBlacklist(url)]
    return urls


async def useAccessibleUrl():
    """
    Check if the url is accessible
    """
    baseUrl1 = "https://www.foodieguide.com/iptvsearch/"
    baseUrl2 = "http://tonkiang.us/"
    speed1 = await getSpeed(baseUrl1, 30)
    speed2 = await getSpeed(baseUrl2, 30)
    if speed1 == float("inf") and speed2 == float("inf"):
        return None
    if speed1 < speed2:
        return baseUrl1
    else:
        return baseUrl2


def getFOFAUrlsFromRegionList():
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


def getChannelsByFOFA(source):
    """
    Get the channel by FOFA
    """
    urls = set(re.findall(r"https?://[\w\.-]+:\d+", source))
    channels = {}
    urls_len = len(urls)
    pbar = tqdm(total=urls_len)
    for url in urls:
        try:
            pbar.set_description(
                f"Processing multicast {url}, {urls_len - pbar.n} urls remaining"
            )
            response = requests.get(url + "/iptv/live/1000.json?key=txiptv", timeout=2)
            try:
                json_data = response.json()
                if json_data["code"] == 0:
                    try:
                        for item in json_data["data"]:
                            if isinstance(item, dict):
                                item_name = formatChannelName(item.get("name"))
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
        finally:
            pbar.update()
    pbar.close()
    return channels


def mergeObjects(*objects):
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
