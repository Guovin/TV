from utils.config import get_config, resource_path
from utils.utils import check_url_by_patterns
from utils.speed import sort_urls_by_speed_and_resolution
import os
from collections import defaultdict
import re
import logging
from logging.handlers import RotatingFileHandler

config = get_config()

handler = RotatingFileHandler("result_new.log", encoding="utf-8")
logging.basicConfig(
    handlers=[handler],
    format="%(message)s",
    level=logging.INFO,
)


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


def append_all_method_data(
    items, data, subscribe_result=None, multicast_result=None, online_search_result=None
):
    """
    Append all method data to total info data
    """
    for cate, channel_obj in items:
        for name, old_urls in channel_obj.items():
            formatName = format_channel_name(name)
            if config.open_subscribe:
                data = append_data_to_info_data(
                    data,
                    cate,
                    name,
                    subscribe_result.get(formatName, []),
                )
                print(
                    name,
                    "subscribe num:",
                    len(subscribe_result.get(formatName, [])),
                )
            if config.open_multicast:
                data = append_data_to_info_data(
                    data,
                    cate,
                    name,
                    multicast_result.get(formatName, []),
                )
                print(
                    name,
                    "multicast num:",
                    len(multicast_result.get(formatName, [])),
                )
            if config.open_online_search:
                data = append_data_to_info_data(
                    data,
                    cate,
                    name,
                    online_search_result.get(formatName, []),
                )
                print(
                    name,
                    "online search num:",
                    len(online_search_result.get(formatName, [])),
                )
            total_channel_data_len = len(data.get(cate, {}).get(name, []))
            print(
                name,
                "total num:",
                total_channel_data_len,
            )
            if total_channel_data_len == 0:
                data = append_data_to_info_data(
                    data,
                    cate,
                    name,
                    [(url, None, None) for url in old_urls],
                )
    return data


async def sort_channel_list(semaphore, name, info_list, callback):
    """
    Sort the channel list
    """
    async with semaphore:
        data = []
        try:
            sorted_data = await sort_urls_by_speed_and_resolution(info_list)
            if sorted_data:
                for (
                    url,
                    date,
                    resolution,
                ), response_time in sorted_data:
                    logging.info(
                        f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time}ms"
                    )
                data = [
                    (url, date, resolution)
                    for (url, date, resolution), _ in sorted_data
                ]
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            callback()
            return {cate, name, data}


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
