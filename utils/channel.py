from utils.config import get_config, resource_path
from utils.tools import check_url_by_patterns, get_total_urls_from_info_list
from utils.speed import sort_urls_by_speed_and_resolution
import os
from collections import defaultdict
import re
from bs4 import NavigableString
import logging
from logging.handlers import RotatingFileHandler
from opencc import OpenCC

config = get_config()

log_dir = "output"
log_file = "result_new.log"
log_path = os.path.join(log_dir, log_file)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

handler = RotatingFileHandler(log_path, encoding="utf-8")
logging.basicConfig(
    handlers=[handler],
    format="%(message)s",
    level=logging.INFO,
)


def get_channel_data_from_file(channels, file):
    """
    Get the channel data from the file
    """
    current_category = ""
    pattern = r"^(.*?),(?!#genre#)(.*?)$"

    for line in file:
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


def get_channel_items():
    """
    Get the channel items from the source file
    """
    user_source_file = config.get("Settings", "source_file")
    user_final_file = config.get("Settings", "final_file")
    channels = defaultdict(lambda: defaultdict(list))

    if os.path.exists(resource_path(user_source_file)):
        with open(resource_path(user_source_file), "r", encoding="utf-8") as file:
            channels = get_channel_data_from_file(channels, file)

    if config.getboolean("Settings", "open_use_old_result") and os.path.exists(
        resource_path(user_final_file)
    ):
        with open(resource_path(user_final_file), "r", encoding="utf-8") as file:
            channels = get_channel_data_from_file(channels, file)

    return channels


def format_channel_name(name):
    """
    Format the channel name with sub and replace and lower
    """
    if config.getboolean("Settings", "open_keep_all"):
        return name
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


def channel_name_is_equal(name1, name2):
    """
    Check if the channel name is equal
    """
    if config.getboolean("Settings", "open_keep_all"):
        return True
    cc = OpenCC("t2s")
    name1_converted = cc.convert(format_channel_name(name1))
    name2_converted = cc.convert(format_channel_name(name2))
    return name1_converted == name2_converted


def get_channel_results_by_name(name, data):
    """
    Get channel results from data by name
    """
    format_name = format_channel_name(name)
    cc1 = OpenCC("s2t")
    converted1 = cc1.convert(format_name)
    cc2 = OpenCC("t2s")
    converted2 = cc2.convert(format_name)
    result1 = data.get(converted1, [])
    result2 = data.get(converted2, [])
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


def get_channel_multicast_total_url_list(url, ip_list):
    """
    Get the channel multicast total url list by url and ip list
    """
    total_url_list = []
    for ip in ip_list:
        total_url = f"http://{url}/rtp/{ip}"
        total_url_list.append(total_url)
    return total_url_list


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
    config_region_list = set(config.get("Settings", "region_list").split(","))
    region_type_list = {
        (region, type)
        for region_type in result.values()
        for region, types in region_type.items()
        if "all" in config_region_list or region in config_region_list
        for type in types
    }
    return list(region_type_list)


def get_channel_multicast_result(result, search_result):
    """
    Get the channel multicast info result by result and search result
    """
    info_result = {}
    for name, result_obj in result.items():
        info_list = [
            (total_url, date, resolution)
            for result_region, result_types in result_obj.items()
            if result_region in search_result
            for result_type, result_type_urls in result_types.items()
            if result_type in search_result[result_region]
            for ip in get_multicast_ip_list(result_type_urls) or []
            for url, date, resolution in search_result[result_region][result_type]
            for total_url in get_channel_multicast_total_url_list(url, [ip])
            if check_url_by_patterns(total_url)
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


def get_results_from_multicast_soup(soup):
    """
    Get the results from the multicast soup
    """
    results = []
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            text = element.strip()
            url = get_channel_url(text)
            if url and not any(item["url"] == url for item in results):
                url_element = soup.find(lambda tag: tag.get_text(strip=True) == url)
                if not url_element:
                    continue

                valid_element = url_element.find_next_sibling()
                if not valid_element:
                    continue

                valid_text = valid_element.get_text(strip=True)
                if "失效" in valid_text:
                    continue

                info_element = valid_element.find_next_sibling().find_next_sibling()
                if not info_element:
                    continue

                info_text = info_element.get_text(strip=True)
                if "上线" in info_text and " " in info_text:
                    date, region, type = get_multicast_channel_info(info_text)
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


def get_results_from_multicast_soup_requests(soup):
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
            results.append({"url": url, "date": date, "region": region, "type": type})

    return results


def update_channel_urls_txt(cate, name, urls):
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


def get_channel_url(text):
    """
    Get the url from text
    """
    url = None
    urlRegex = r"((http|https)://)?((([0-9]{1,3}\.){3}[0-9]{1,3})|([a-zA-Z0-9-]+\.[a-zA-Z]{2,}))(:[0-9]+)?(/[a-zA-Z0-9-._~:/?#[\]@!$&'()*+,;=%]*)?"
    url_search = re.search(
        urlRegex,
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
    return data


def append_data_to_info_data(info_data, cate, name, data, check=True):
    """
    Append channel data to total info data
    """
    info_data = init_info_data(info_data, cate, name)
    for url, date, resolution in data:
        if (url and not check) or (url and check and check_url_by_patterns(url)):
            info_data[cate][name].append((url, date, resolution))
    return info_data


def append_total_data(*args, **kwargs):
    """
    Append total channel data
    """
    if config.getboolean("Settings", "open_keep_all"):
        return append_all_method_data_keep_all(*args, **kwargs)
    else:
        return append_all_method_data(*args, **kwargs)


def append_all_method_data(
    items, data, subscribe_result=None, multicast_result=None, online_search_result=None
):
    """
    Append all method data to total info data
    """
    for cate, channel_obj in items:
        for name, old_urls in channel_obj.items():
            for method, result in [
                ("subscribe", subscribe_result),
                ("multicast", multicast_result),
                ("online_search", online_search_result),
            ]:
                if config.getboolean("Settings", f"open_{method}"):
                    data = append_data_to_info_data(
                        data,
                        cate,
                        name,
                        get_channel_results_by_name(name, result),
                    )
                    print(
                        name,
                        f"{method.capitalize()} num:",
                        len(get_channel_results_by_name(name, result)),
                    )
            total_channel_data_len = len(data.get(cate, {}).get(name, []))
            if total_channel_data_len == 0 or config.getboolean(
                "Settings", "open_use_old_result"
            ):
                data = append_data_to_info_data(
                    data,
                    cate,
                    name,
                    [(url, None, None) for url in old_urls],
                )
            print(
                name,
                "total num:",
                len(data.get(cate, {}).get(name, [])),
            )
    return data


def append_all_method_data_keep_all(
    items, data, subscribe_result=None, multicast_result=None, online_search_result=None
):
    """
    Append all method data to total info data, keep all channel name and urls
    """
    for cate, channel_obj in items:
        for result_name, result in [
            ("subscribe", subscribe_result),
            ("multicast", multicast_result),
            ("online_search", online_search_result),
        ]:
            if result and config.getboolean("Settings", f"open_{result_name}"):
                for name, urls in result.items():
                    data = append_data_to_info_data(data, cate, name, urls)
                    print(name, f"{result_name.capitalize()} num:", len(urls))
                    if config.getboolean("Settings", "open_use_old_result"):
                        old_urls = channel_obj.get(name, [])
                        data = append_data_to_info_data(
                            data,
                            cate,
                            name,
                            [(url, None, None) for url in old_urls],
                        )

    return data


async def sort_channel_list(semaphore, cate, name, info_list, is_ffmpeg, callback):
    """
    Sort the channel list
    """
    async with semaphore:
        data = []
        try:
            if info_list:
                sorted_data = await sort_urls_by_speed_and_resolution(
                    info_list, is_ffmpeg
                )
                if sorted_data:
                    for (
                        url,
                        date,
                        resolution,
                    ), response_time in sorted_data:
                        logging.info(
                            f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time} ms"
                        )
                    data = [
                        (url, date, resolution)
                        for (url, date, resolution), _ in sorted_data
                    ]
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            callback()
            return {"cate": cate, "name": name, "data": data}


def write_channel_to_file(items, data, callback):
    """
    Write channel to file
    """
    for cate, channel_obj in items:
        for name in channel_obj.keys():
            info_list = data.get(cate, {}).get(name, [])
            try:
                channel_urls = get_total_urls_from_info_list(info_list)
                print("write:", cate, name, "num:", len(channel_urls))
                update_channel_urls_txt(cate, name, channel_urls)
            finally:
                callback()
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)
