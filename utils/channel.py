from utils.config import config, resource_path
from utils.tools import (
    check_url_by_patterns,
    get_total_urls_from_info_list,
    process_nested_dict,
    get_resolution_value,
)
from utils.speed import (
    sort_urls_by_speed_and_resolution,
    is_ffmpeg_installed,
    add_info_url,
    speed_cache,
)
import os
from collections import defaultdict
import re
from bs4 import NavigableString
import logging
from logging.handlers import RotatingFileHandler
from opencc import OpenCC
import asyncio
import base64
import pickle
import copy
import datetime

log_dir = "output"
log_file = "result_new.log"
log_path = os.path.join(log_dir, log_file)
handler = None

url_regex = r"\b((https?):\/\/)?(\[[0-9a-fA-F:]+\]|([\w-]+\.)+[\w-]+)(:[0-9]{1,5})?(\/[^\s]*)?\b"
rtp_regex = r"^(.*?),(rtp://.*)?$"
txt_regex = r"^(.*?)(?:,)?((?!#genre#)" + url_regex + r")?$"
m3u_regex = r"^#EXTINF:-1.*?,(.*?)\n" + url_regex + r"$"


def setup_logging():
    """
    Setup logging
    """
    global handler
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    handler = RotatingFileHandler(log_path, encoding="utf-8")
    logging.basicConfig(
        handlers=[handler],
        format="%(message)s",
        level=logging.INFO,
    )


def cleanup_logging():
    """
    Cleanup logging
    """
    global handler
    if handler:
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
    if os.path.exists(log_path):
        os.remove(log_path)


def get_name_url(content, m3u=False, rtp=False, check_url=True):
    """
    Get channel name and url from content
    """
    regex = m3u_regex if m3u else rtp_regex if rtp else txt_regex
    matches = re.findall(regex, content, re.MULTILINE)
    channels = [
        {"name": match[0].strip(), "url": match[1].strip()}
        for match in matches
        if (check_url and match[1].strip()) or not check_url
    ]
    return channels


def get_channel_data_from_file(channels, file, use_old):
    """
    Get the channel data from the file
    """
    current_category = ""

    for line in file:
        line = line.strip()
        if "#genre#" in line:
            current_category = line.split(",")[0]
        else:
            name_url = get_name_url(line, check_url=False)
            if name_url and name_url[0]:
                name = name_url[0]["name"]
                url = name_url[0]["url"]
                category_dict = channels[current_category]
                if name not in category_dict:
                    category_dict[name] = []
                if use_old and url:
                    info = (url, None, None, None)
                    if info[0] and info not in category_dict[name]:
                        category_dict[name].append(info)
    return channels


def get_channel_items():
    """
    Get the channel items from the source file
    """
    user_source_file = config.get("Settings", "source_file", fallback="config/demo.txt")
    channels = defaultdict(lambda: defaultdict(list))
    open_use_old_result = config.getboolean(
        "Settings", "open_use_old_result", fallback=True
    )

    if os.path.exists(resource_path(user_source_file)):
        with open(resource_path(user_source_file), "r", encoding="utf-8") as file:
            channels = get_channel_data_from_file(channels, file, open_use_old_result)

    if open_use_old_result:
        result_cache_path = resource_path("output/result_cache.pkl")
        if os.path.exists(result_cache_path):
            with open(resource_path("output/result_cache.pkl"), "rb") as file:
                old_result = pickle.load(file)
                for cate, data in channels.items():
                    if cate in old_result:
                        for name, info_list in data.items():
                            if name in old_result[cate]:
                                for info in old_result[cate][name]:
                                    if info not in info_list:
                                        channels[cate][name].append(info)
    return channels


open_keep_all = config.getboolean("Settings", "open_keep_all", fallback=False)


def format_channel_name(name):
    """
    Format the channel name with sub and replace and lower
    """
    if open_keep_all:
        return name
    cc = OpenCC("t2s")
    name = cc.convert(name)
    sub_pattern = r"-|_|\((.*?)\)|\（(.*?)\）|\[(.*?)\]|\「(.*?)\」| |｜|频道|普清|标清|高清|HD|hd|超清|超高|超高清|中央|央视|台|电信|联通|移动"
    name = re.sub(sub_pattern, "", name)
    replace_dict = {
        "plus": "+",
        "PLUS": "+",
        "＋": "+",
        "CCTV1综合": "CCTV1",
        "CCTV2财经": "CCTV2",
        "CCTV3综艺": "CCTV3",
        "CCTV4国际": "CCTV4",
        "CCTV4中文国际": "CCTV4",
        "CCTV4欧洲": "CCTV4",
        "CCTV5体育": "CCTV5",
        "CCTV5+体育赛视": "CCTV5+",
        "CCTV5+体育赛事": "CCTV5+",
        "CCTV5+体育": "CCTV5+",
        "CCTV6电影": "CCTV6",
        "CCTV7军事": "CCTV7",
        "CCTV7军农": "CCTV7",
        "CCTV7农业": "CCTV7",
        "CCTV7国防军事": "CCTV7",
        "CCTV8电视剧": "CCTV8",
        "CCTV9记录": "CCTV9",
        "CCTV9纪录": "CCTV9",
        "CCTV10科教": "CCTV10",
        "CCTV11戏曲": "CCTV11",
        "CCTV12社会与法": "CCTV12",
        "CCTV13新闻": "CCTV13",
        "CCTV新闻": "CCTV13",
        "CCTV14少儿": "CCTV14",
        "CCTV15音乐": "CCTV15",
        "CCTV16奥林匹克": "CCTV16",
        "CCTV17农业农村": "CCTV17",
        "CCTV17农业": "CCTV17",
    }
    for old, new in replace_dict.items():
        name = name.replace(old, new)
    return name.lower()


def channel_name_is_equal(name1, name2):
    """
    Check if the channel name is equal
    """
    if open_keep_all:
        return True
    name1_format = format_channel_name(name1)
    name2_format = format_channel_name(name2)
    return name1_format == name2_format


def get_channel_results_by_name(name, data):
    """
    Get channel results from data by name
    """
    format_name = format_channel_name(name)
    cc = OpenCC("s2t")
    name_s2t = cc.convert(format_name)
    result1 = data.get(format_name, [])
    result2 = data.get(name_s2t, [])
    results = list(dict.fromkeys(result1 + result2))
    return results


def get_element_child_text_list(element, child_name):
    """
    Get the child text of the element
    """
    text_list = []
    children = element.find_all(child_name)
    if children:
        for child in children:
            text = child.get_text(strip=True)
            if text:
                text_list.append(text)
    return text_list


def get_multicast_ip_list(urls):
    """
    Get the multicast ip list from urls
    """
    ip_list = []
    for url in urls:
        pattern = r"rtp://((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?)"
        matcher = re.search(pattern, url)
        if matcher:
            ip_list.append(matcher.group(1))
    return ip_list


def get_channel_multicast_region_ip_list(result, channel_region, channel_type):
    """
    Get the channel multicast region ip list by region and type from result
    """
    return [
        ip
        for result_region, result_obj in result.items()
        if result_region in channel_region
        for type, urls in result_obj.items()
        if type in channel_type
        for ip in get_multicast_ip_list(urls)
    ]


def get_channel_multicast_name_region_type_result(result, names):
    """
    Get the multicast name and region and type result by names from result
    """
    name_region_type_result = {}
    for name in names:
        format_name = format_channel_name(name)
        data = result.get(format_name)
        if data:
            name_region_type_result[format_name] = data
    return name_region_type_result


def get_channel_multicast_region_type_list(result):
    """
    Get the channel multicast region type list from result
    """
    config_region_list = set(
        region.strip()
        for region in config.get(
            "Settings", "multicast_region_list", fallback="全部"
        ).split(",")
        if region.strip()
    )
    region_type_list = {
        (region, type)
        for region_type in result.values()
        for region, types in region_type.items()
        if "all" in config_region_list
        or "ALL" in config_region_list
        or "全部" in config_region_list
        or region in config_region_list
        for type in types
    }
    return list(region_type_list)


def get_channel_multicast_result(result, search_result):
    """
    Get the channel multicast info result by result and search result
    """
    info_result = {}
    open_sort = config.getboolean("Settings", "open_sort", fallback=True)
    for name, result_obj in result.items():
        info_list = [
            (
                (
                    f"http://{url}/rtp/{ip}$cache:{url}"
                    if open_sort
                    else f"http://{url}/rtp/{ip}"
                ),
                date,
                resolution,
            )
            for result_region, result_types in result_obj.items()
            if result_region in search_result
            for result_type, result_type_urls in result_types.items()
            if result_type in search_result[result_region]
            for ip in get_multicast_ip_list(result_type_urls) or []
            for url, date, resolution in search_result[result_region][result_type]
            if check_url_by_patterns(f"http://{url}/rtp/{ip}")
        ]
        info_result[name] = info_list
    return info_result


def get_results_from_soup(soup, name):
    """
    Get the results from the soup
    """
    results = []
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            text = element.get_text(strip=True)
            url = get_channel_url(text)
            if url and not any(item[0] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if url_element:
                    name_element = url_element.find_previous_sibling()
                    if name_element:
                        channel_name = name_element.get_text(strip=True)
                        if channel_name_is_equal(name, channel_name):
                            info_element = url_element.find_next_sibling()
                            date, resolution = get_channel_info(
                                info_element.get_text(strip=True)
                            )
                            results.append((url, date, resolution))
    return results


def get_results_from_multicast_soup(soup, hotel=False):
    """
    Get the results from the multicast soup
    """
    results = []
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            text = element.strip()
            if "失效" in text:
                continue
            url = get_channel_url(text)
            if url and not any(item["url"] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if not url_element:
                    continue
                parent_element = url_element.find_parent()
                info_element = parent_element.find_all(recursive=False)[-1]
                if not info_element:
                    continue
                info_text = info_element.get_text(strip=True)
                if "上线" in info_text and " " in info_text:
                    date, region, type = get_multicast_channel_info(info_text)
                    if hotel and "酒店" not in region:
                        continue
                    results.append(
                        {
                            "url": url,
                            "date": date,
                            "region": region,
                            "type": type,
                        }
                    )
    return results


def get_results_from_soup_requests(soup, name):
    """
    Get the results from the soup by requests
    """
    results = []
    elements = soup.find_all("div", class_="resultplus") if soup else []
    for element in elements:
        name_element = element.find("div", class_="channel")
        if name_element:
            channel_name = name_element.get_text(strip=True)
            if channel_name_is_equal(name, channel_name):
                text_list = get_element_child_text_list(element, "div")
                url = date = resolution = None
                for text in text_list:
                    text_url = get_channel_url(text)
                    if text_url:
                        url = text_url
                    if " " in text:
                        text_info = get_channel_info(text)
                        date, resolution = text_info
                if url:
                    results.append((url, date, resolution))
    return results


def get_results_from_multicast_soup_requests(soup, hotel=False):
    """
    Get the results from the multicast soup by requests
    """
    results = []
    if not soup:
        return results

    elements = soup.find_all("div", class_="result")
    for element in elements:
        name_element = element.find("div", class_="channel")
        if not name_element:
            continue

        text_list = get_element_child_text_list(element, "div")
        url, date, region, type = None, None, None, None
        valid = True

        for text in text_list:
            if "失效" in text:
                valid = False
                break

            text_url = get_channel_url(text)
            if text_url:
                url = text_url

            if url and "上线" in text and " " in text:
                date, region, type = get_multicast_channel_info(text)

        if url and valid:
            if hotel and "酒店" not in region:
                continue
            results.append({"url": url, "date": date, "region": region, "type": type})

    return results


def update_channel_urls_txt(cate, name, urls, callback=None):
    """
    Update the category and channel urls to the final file
    """
    genre_line = cate + ",#genre#\n"
    filename = "output/result_new.txt"

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
                if callback:
                    callback()


def get_channel_url(text):
    """
    Get the url from text
    """
    url = None
    url_search = re.search(
        url_regex,
        text,
    )
    if url_search:
        url = url_search.group().strip()
    return url


def get_channel_info(text):
    """
    Get the channel info from text
    """
    date, resolution = None, None
    if text:
        date, resolution = (
            (text.partition(" ")[0] if text.partition(" ")[0] else None),
            (
                text.partition(" ")[2].partition("•")[2]
                if text.partition(" ")[2].partition("•")[2]
                else None
            ),
        )
    return date, resolution


def get_multicast_channel_info(text):
    """
    Get the multicast channel info from text
    """
    date, region, type = None, None, None
    if text:
        text_split = text.split(" ")
        filtered_data = list(filter(lambda x: x.strip() != "", text_split))
        if filtered_data and len(filtered_data) == 4:
            date = filtered_data[0]
            region = filtered_data[2]
            type = filtered_data[3]
    return date, region, type


def init_info_data(data, cate, name):
    """
    Init channel info data
    """
    if data.get(cate) is None:
        data[cate] = {}
    if data[cate].get(name) is None:
        data[cate][name] = []


def append_data_to_info_data(info_data, cate, name, data, origin=None, check=True):
    """
    Append channel data to total info data
    """
    init_info_data(info_data, cate, name)
    for item in data:
        try:
            url, date, resolution, *rest = item
            origin = origin or (rest[0] if rest else None)
            if (url and not check) or (url and check and check_url_by_patterns(url)):
                info_data[cate][name].append((url, date, resolution, origin))
        except:
            continue


def append_total_data(*args, **kwargs):
    """
    Append total channel data
    """
    if open_keep_all:
        append_all_method_data_keep_all(*args, **kwargs)
    else:
        append_all_method_data(*args, **kwargs)


def append_all_method_data(
    items,
    data,
    hotel_fofa_result=None,
    multicast_result=None,
    hotel_tonkiang_result=None,
    subscribe_result=None,
    online_search_result=None,
):
    """
    Append all method data to total info data
    """
    for cate, channel_obj in items:
        for name, old_info_list in channel_obj.items():
            print(f"{name}:", end=" ")
            for method, result in [
                ("hotel_fofa", hotel_fofa_result),
                ("multicast", multicast_result),
                ("hotel_tonkiang", hotel_tonkiang_result),
                ("subscribe", subscribe_result),
                ("online_search", online_search_result),
            ]:
                if config.getboolean("Settings", f"open_{method}", fallback=None):
                    if (
                        method == "hotel_tonkiang" or method == "hotel_fofa"
                    ) and config.getboolean(
                        "Settings", f"open_hotel", fallback=True
                    ) == False:
                        continue
                    name_results = get_channel_results_by_name(name, result)
                    origin_method = (
                        "hotel"
                        if method == "hotel_tonkiang" or method == "hotel_fofa"
                        else method
                    )
                    append_data_to_info_data(
                        data, cate, name, name_results, origin=origin_method
                    )
                    print(f"{method.capitalize()}:", len(name_results), end=", ")
            total_channel_data_len = len(data.get(cate, {}).get(name, []))
            if total_channel_data_len == 0 or config.getboolean(
                "Settings", "open_use_old_result", fallback=True
            ):
                append_data_to_info_data(
                    data,
                    cate,
                    name,
                    old_info_list,
                )
                print("old:", len(old_info_list), end=", ")
            print(
                "total:",
                len(data.get(cate, {}).get(name, [])),
            )


def append_all_method_data_keep_all(
    items,
    data,
    hotel_fofa_result=None,
    multicast_result=None,
    hotel_tonkiang_result=None,
    subscribe_result=None,
    online_search_result=None,
):
    """
    Append all method data to total info data, keep all channel name and urls
    """
    for cate, channel_obj in items:
        for method, result in [
            ("hotel_fofa", hotel_fofa_result),
            ("multicast", multicast_result),
            ("hotel_tonkiang", hotel_tonkiang_result),
            ("subscribe", subscribe_result),
            ("online_search", online_search_result),
        ]:
            if result and config.getboolean(
                "Settings", f"open_{method}", fallback=None
            ):
                if (
                    method == "hotel_tonkiang" or method == "hotel_fofa"
                ) and config.getboolean(
                    "Settings", f"open_hotel", fallback=True
                ) == False:
                    continue
                origin_method = (
                    "hotel"
                    if method == "hotel_tonkiang" or method == "hotel_fofa"
                    else method
                )
                for name, urls in result.items():
                    print(f"{name}:", end=" ")
                    append_data_to_info_data(
                        data, cate, name, urls, origin=origin_method
                    )
                    print(name, f"{method.capitalize()}:", len(urls), end=", ")
                    if config.getboolean(
                        "Settings", "open_use_old_result", fallback=True
                    ):
                        old_info_list = channel_obj.get(name, [])
                        append_data_to_info_data(
                            data,
                            cate,
                            name,
                            old_info_list,
                        )
                        print(name, "old:", len(old_info_list), end=", ")
                    print(
                        "total:",
                        len(data.get(cate, {}).get(name, [])),
                    )


async def sort_channel_list(
    cate,
    name,
    info_list,
    semaphore,
    ffmpeg=False,
    ipv6_proxy=None,
    filter_resolution=False,
    min_resolution=None,
    callback=None,
):
    """
    Sort the channel list
    """
    async with semaphore:
        data = []
        try:
            if info_list:
                sorted_data = await sort_urls_by_speed_and_resolution(
                    info_list, ffmpeg=ffmpeg, ipv6_proxy=ipv6_proxy, callback=callback
                )
                if sorted_data:
                    for (url, date, resolution, origin), response_time in sorted_data:
                        if resolution and filter_resolution:
                            resolution_value = get_resolution_value(resolution)
                            if resolution_value < min_resolution:
                                continue
                        logging.info(
                            f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time} ms"
                        )
                        data.append((url, date, resolution, origin))
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            return {"cate": cate, "name": name, "data": data}


async def process_sort_channel_list(data, ipv6=False, callback=None):
    """
    Processs the sort channel list
    """
    open_ffmpeg = config.getboolean("Settings", "open_ffmpeg", fallback=True)
    ipv_type = config.get("Settings", "ipv_type", fallback="全部").lower()
    open_filter_resolution = config.getboolean(
        "Settings", "open_filter_resolution", fallback=True
    )
    min_resolution = get_resolution_value(
        config.get("Settings", "min_resolution", fallback="1920x1080")
    )
    open_ipv6 = "ipv6" in ipv_type or "all" in ipv_type or "全部" in ipv_type
    ipv6_proxy = None if not open_ipv6 or ipv6 else "http://www.ipv6proxy.net/go.php?u="
    ffmpeg_installed = is_ffmpeg_installed()
    if open_ffmpeg and not ffmpeg_installed:
        print("FFmpeg is not installed, using requests for sorting.")
    is_ffmpeg = open_ffmpeg and ffmpeg_installed
    semaphore = asyncio.Semaphore(5)
    need_sort_data = copy.deepcopy(data)
    process_nested_dict(need_sort_data, seen=set(), flag="$cache:")
    tasks = [
        asyncio.create_task(
            sort_channel_list(
                cate,
                name,
                info_list,
                semaphore,
                ffmpeg=is_ffmpeg,
                ipv6_proxy=ipv6_proxy,
                filter_resolution=open_filter_resolution,
                min_resolution=min_resolution,
                callback=callback,
            )
        )
        for cate, channel_obj in need_sort_data.items()
        for name, info_list in channel_obj.items()
    ]
    sort_results = await asyncio.gather(*tasks)
    sort_data = {}
    for result in sort_results:
        if result:
            cate, name, result_data = result["cate"], result["name"], result["data"]
            append_data_to_info_data(sort_data, cate, name, result_data, check=False)
    for cate, obj in data.items():
        for name, info_list in obj.items():
            sort_info_list = sort_data.get(cate, {}).get(name, [])
            sort_urls = {
                sort_url[0].split("$")[0]
                for sort_url in sort_info_list
                if sort_url and sort_url[0]
            }
            for url, date, resolution, origin in info_list:
                url_rsplit = url.rsplit("$cache:", 1)
                if len(url_rsplit) != 2:
                    continue
                url, cache_key = url_rsplit
                url = url.split("$")[0]
                if url in sort_urls or cache_key not in speed_cache:
                    continue
                cache = speed_cache[cache_key]
                if not cache:
                    continue
                response_time, resolution = cache
                if response_time and response_time != float("inf"):
                    if resolution:
                        url = add_info_url(url, resolution)
                        if open_filter_resolution:
                            resolution_value = get_resolution_value(resolution)
                            if resolution_value < min_resolution:
                                continue
                    append_data_to_info_data(
                        sort_data,
                        cate,
                        name,
                        [(url, date, resolution, origin)],
                        check=False,
                    )
                    logging.info(
                        f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time} ms"
                    )
    return sort_data


def write_channel_to_file(items, data, ipv6=False, callback=None):
    """
    Write channel to file
    """
    open_update_time = config.getboolean("Settings", "open_update_time", fallback=True)
    if open_update_time:
        now = datetime.datetime.now()
        if os.environ.get("GITHUB_ACTIONS"):
            now += datetime.timedelta(hours=8)
        update_time = now.strftime("%Y-%m-%d %H:%M:%S")
        update_channel_urls_txt("更新时间", f"{update_time}", ["url"])
    result_items = (
        data.items()
        if config.getboolean("Settings", "open_keep_all", fallback=False)
        else items
    )
    for cate, channel_obj in result_items:
        print(f"\n{cate}:", end=" ")
        channel_obj_keys = channel_obj.keys()
        names_len = len(list(channel_obj_keys))
        for i, name in enumerate(channel_obj_keys):
            info_list = data.get(cate, {}).get(name, [])
            channel_urls = get_total_urls_from_info_list(info_list, ipv6=ipv6)
            end_char = ", " if i < names_len - 1 else ""
            print(f"{name}:", len(channel_urls), end=end_char)
            update_channel_urls_txt(cate, name, channel_urls, callback=callback)
        print()


def get_multicast_fofa_search_org(region, type):
    """
    Get the fofa search organization for multicast
    """
    org = None
    if region == "北京" and type == "联通":
        org = "China Unicom Beijing Province Network"
    elif type == "联通":
        org = "CHINA UNICOM China169 Backbone"
    elif type == "电信":
        org = "Chinanet"
    elif type == "移动":
        org == "China Mobile communications corporation"
    return org


def get_multicast_fofa_search_urls():
    """
    Get the fofa search urls for multicast
    """
    config_region_list = [
        region.strip()
        for region in config.get(
            "Settings", "multicast_region_list", fallback="全部"
        ).split(",")
        if region.strip()
    ]
    rtp_file_names = []
    for filename in os.listdir(resource_path("config/rtp")):
        if filename.endswith(".txt") and "_" in filename:
            filename = filename.replace(".txt", "")
            rtp_file_names.append(filename)
    region_type_list = [
        (parts[0], parts[1])
        for name in rtp_file_names
        if (parts := name.split("_"))[0] in config_region_list
        or "all" in config_region_list
        or "ALL" in config_region_list
        or "全部" in config_region_list
    ]
    search_urls = []
    for region, type in region_type_list:
        search_url = "https://fofa.info/result?qbase64="
        search_txt = f'"udpxy" && country="CN" && region="{region}" && org="{get_multicast_fofa_search_org(region,type)}"'
        bytes_string = search_txt.encode("utf-8")
        search_txt = base64.b64encode(bytes_string).decode("utf-8")
        search_url += search_txt
        search_urls.append((search_url, region, type))
    return search_urls


def get_channel_data_cache_with_compare(data, new_data):
    """
    Get channel data with cache compare new data
    """
    for cate, obj in new_data.items():
        for name, url_info in obj.items():
            if url_info and cate in data and name in data[cate]:
                new_urls = {
                    new_url.split("$", 1)[0]: new_resolution
                    for new_url, _, new_resolution, _ in url_info
                }
                updated_data = []
                for info in data[cate][name]:
                    url, date, resolution, origin = info
                    base_url = url.split("$", 1)[0]
                    if base_url in new_urls:
                        resolution = new_urls[base_url]
                        updated_data.append((url, date, resolution, origin))
                data[cate][name] = updated_data


def format_channel_url_info(data):
    """
    Format channel url info, remove cache, add resolution to url
    """
    for obj in data.values():
        for url_info in obj.values():
            for i, (url, date, resolution, origin) in enumerate(url_info):
                url = url.split("$", 1)[0]
                if resolution:
                    url = add_info_url(url, resolution)
                url_info[i] = (url, date, resolution, origin)
