from time import time
import datetime
import os
import urllib.parse
import ipaddress
import socket
from utils.config import config
import utils.constants as constants
import re
from bs4 import BeautifulSoup
from flask import render_template_string, send_file
import shutil
import requests
import sys
import logging
from logging.handlers import RotatingFileHandler


def get_logger(path, level=logging.ERROR, init=False):
    """
    get the logger
    """
    if not os.path.exists(constants.output_dir):
        os.makedirs(constants.output_dir)
    if init and os.path.exists(path):
        os.remove(path)
    handler = RotatingFileHandler(path, encoding="utf-8")
    logger = logging.getLogger(path)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def format_interval(t):
    """
    Formats a number of seconds as a clock time, [H:]MM:SS

    Parameters
    ----------
    t  : int or float
        Number of seconds.
    Returns
    -------
    out  : str
        [H:]MM:SS
    """
    mins, s = divmod(int(t), 60)
    h, m = divmod(mins, 60)
    if h:
        return "{0:d}:{1:02d}:{2:02d}".format(h, m, s)
    else:
        return "{0:02d}:{1:02d}".format(m, s)


def get_pbar_remaining(n=0, total=0, start_time=None):
    """
    Get the remaining time of the progress bar
    """
    try:
        elapsed = time() - start_time
        completed_tasks = n
        if completed_tasks > 0:
            avg_time_per_task = elapsed / completed_tasks
            remaining_tasks = total - completed_tasks
            remaining_time = format_interval(avg_time_per_task * remaining_tasks)
        else:
            remaining_time = "未知"
        return remaining_time
    except Exception as e:
        print(f"Error: {e}")


def update_file(final_file, old_file, copy=False):
    """
    Update the file
    """
    old_file_path = resource_path(old_file, persistent=True)
    final_file_path = resource_path(final_file, persistent=True)
    if os.path.exists(old_file_path):
        if copy:
            shutil.copyfile(old_file_path, final_file_path)
        else:
            os.replace(old_file_path, final_file_path)


def filter_by_date(data):
    """
    Filter by date and limit
    """
    default_recent_days = 30
    use_recent_days = config.recent_days
    if not isinstance(use_recent_days, int) or use_recent_days <= 0:
        use_recent_days = default_recent_days
    start_date = datetime.datetime.now() - datetime.timedelta(days=use_recent_days)
    recent_data = []
    unrecent_data = []
    for (url, date, resolution, origin), response_time in data:
        item = ((url, date, resolution, origin), response_time)
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


def get_soup(source):
    """
    Get soup from source
    """
    source = re.sub(
        r"<!--.*?-->",
        "",
        source,
        flags=re.DOTALL,
    )
    soup = BeautifulSoup(source, "html.parser")
    return soup


def get_resolution_value(resolution_str):
    """
    Get resolution value from string
    """
    pattern = r"(\d+)[xX*](\d+)"
    match = re.search(pattern, resolution_str)
    if match:
        width, height = map(int, match.groups())
        return width * height
    else:
        return 0


def get_total_urls_from_info_list(infoList, ipv6=False):
    """
    Get the total urls from info list
    """
    ipv_type_prefer = list(config.ipv_type_prefer)
    if "自动" in ipv_type_prefer or "auto" in ipv_type_prefer or not ipv_type_prefer:
        ipv_type_prefer = ["ipv6", "ipv4"] if ipv6 else ["ipv4", "ipv6"]
    origin_type_prefer = config.origin_type_prefer
    categorized_urls = {
        origin: {"ipv4": [], "ipv6": []} for origin in origin_type_prefer
    }

    total_urls = []
    for url, _, resolution, origin in infoList:
        if not origin:
            continue

        if origin == "important":
            im_url, _, im_info = url.partition("$")
            im_info_value = im_info.partition("!")[2]
            total_urls.append(f"{im_url}${im_info_value}" if im_info_value else im_url)
            continue

        if origin == "subscribe" and "/rtp/" in url:
            origin = "multicast"

        if origin not in origin_type_prefer:
            continue

        if config.open_filter_resolution and resolution:
            resolution_value = get_resolution_value(resolution)
            if resolution_value < config.min_resolution_value:
                continue

        pure_url, _, info = url.partition("$")
        if not info:
            origin_name = constants.origin_map[origin]
            if origin_name:
                url = add_url_info(pure_url, origin_name)

        url_is_ipv6 = is_ipv6(url)
        if url_is_ipv6:
            url = add_url_info(url, "IPv6")

        if resolution:
            url = add_url_info(url, resolution)

        if url_is_ipv6:
            categorized_urls[origin]["ipv6"].append(url)
        else:
            categorized_urls[origin]["ipv4"].append(url)

    ipv_num = {
        "ipv4": 0,
        "ipv6": 0,
    }
    urls_limit = config.urls_limit
    for origin in origin_type_prefer:
        if len(total_urls) >= urls_limit:
            break
        for ipv_type in ipv_type_prefer:
            if len(total_urls) >= urls_limit:
                break
            if ipv_num[ipv_type] < config.ipv_limit[ipv_type]:
                limit = min(
                    config.source_limits[origin] - ipv_num[ipv_type],
                    config.ipv_limit[ipv_type] - ipv_num[ipv_type],
                )
                urls = categorized_urls[origin][ipv_type][:limit]
                total_urls.extend(urls)
                ipv_num[ipv_type] += len(urls)
            else:
                continue

    ipv_type_total = list(dict.fromkeys(ipv_type_prefer + ["ipv4", "ipv6"]))
    if len(total_urls) < urls_limit:
        for origin in origin_type_prefer:
            if len(total_urls) >= urls_limit:
                break
            for ipv_type in ipv_type_total:
                if len(total_urls) >= urls_limit:
                    break
                extra_urls = categorized_urls[origin][ipv_type][
                    : config.source_limits[origin]
                ]
                total_urls.extend(extra_urls)
                total_urls = list(dict.fromkeys(total_urls))[:urls_limit]

    total_urls = list(dict.fromkeys(total_urls))[:urls_limit]

    if not config.open_url_info:
        return [url.partition("$")[0] for url in total_urls]
    else:
        return total_urls


def get_total_urls_from_sorted_data(data):
    """
    Get the total urls with filter by date and depulicate from sorted data
    """
    total_urls = []
    if len(data) > config.urls_limit:
        total_urls = [url for (url, _, _, _), _ in filter_by_date(data)]
    else:
        total_urls = [url for (url, _, _, _), _ in data]
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


def check_ipv6_support():
    """
    Check if the system network supports ipv6
    """
    url = "https://ipv6.tokyo.test-ipv6.com/ip/?callback=?&testdomain=test-ipv6.com&testname=test_aaaa"
    try:
        print("Checking if your network supports IPv6...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("Your network supports IPv6")
            return True
    except Exception:
        pass
    print("Your network does not support IPv6")
    return False


def check_url_ipv_type(url):
    """
    Check if the url is compatible with the ipv type in the config
    """
    ipv6 = is_ipv6(url)
    ipv_type = config.ipv_type
    return (
        (ipv_type == "ipv4" and not ipv6)
        or (ipv_type == "ipv6" and ipv6)
        or ipv_type == "全部"
        or ipv_type == "all"
    )


def check_by_url_keywords_blacklist(url):
    """
    Check by URL blacklist keywords
    """
    return not any(keyword in url for keyword in config.url_keywords_blacklist)


def check_url_by_patterns(url):
    """
    Check the url by patterns
    """
    return check_url_ipv_type(url) and check_by_url_keywords_blacklist(url)


def filter_urls_by_patterns(urls):
    """
    Filter urls by patterns
    """
    urls = [url for url in urls if check_url_ipv_type(url)]
    urls = [url for url in urls if check_by_url_keywords_blacklist(url)]
    return urls


def merge_objects(*objects):
    """
    Merge objects
    """

    def merge_dicts(dict1, dict2):
        for key, value in dict2.items():
            if key in dict1:
                if isinstance(dict1[key], dict) and isinstance(value, dict):
                    merge_dicts(dict1[key], value)
                elif isinstance(dict1[key], set):
                    dict1[key].update(value)
                elif isinstance(dict1[key], list):
                    if value:
                        dict1[key].extend(value)
                        dict1[key] = list(set(dict1[key]))
                elif value:
                    dict1[key] = {dict1[key], value}
            else:
                dict1[key] = value

    merged_dict = {}
    for obj in objects:
        if not isinstance(obj, dict):
            raise TypeError("All input objects must be dictionaries")
        merge_dicts(merged_dict, obj)

    return merged_dict


def get_ip_address():
    """
    Get the IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return f"http://{IP}:8000"


def convert_to_m3u():
    """
    Convert result txt to m3u format
    """
    user_final_file = resource_path(config.final_file)
    if os.path.exists(user_final_file):
        with open(user_final_file, "r", encoding="utf-8") as file:
            m3u_output = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n'
            current_group = None
            for line in file:
                trimmed_line = line.strip()
                if trimmed_line != "":
                    if "#genre#" in trimmed_line:
                        current_group = trimmed_line.replace(",#genre#", "").strip()
                    else:
                        try:
                            original_channel_name, _, channel_link = map(
                                str.strip, trimmed_line.partition(",")
                            )
                        except:
                            continue
                        processed_channel_name = re.sub(
                            r"(CCTV|CETV)-(\d+)(\+.*)?",
                            lambda m: f"{m.group(1)}{m.group(2)}"
                            + ("+" if m.group(3) else ""),
                            original_channel_name,
                        )
                        m3u_output += f'#EXTINF:-1 tvg-name="{processed_channel_name}" tvg-logo="https://live.fanmingming.com/tv/{processed_channel_name}.png"'
                        if current_group:
                            m3u_output += f' group-title="{current_group}"'
                        m3u_output += f",{original_channel_name}\n{channel_link}\n"
            m3u_file_path = os.path.splitext(user_final_file)[0] + ".m3u"
            with open(m3u_file_path, "w", encoding="utf-8") as m3u_file:
                m3u_file.write(m3u_output)
            print(f"✅ M3U result file generated at: {m3u_file_path}")


def get_result_file_content(show_content=False, file_type=None):
    """
    Get the content of the result file
    """
    user_final_file = resource_path(config.final_file)
    result_file = (
        os.path.splitext(user_final_file)[0] + f".{file_type}"
        if file_type
        else user_final_file
    )
    if os.path.exists(result_file):
        if config.open_m3u_result:
            if file_type == "m3u" or not file_type:
                result_file = os.path.splitext(user_final_file)[0] + ".m3u"
            if file_type != "txt" and show_content == False:
                return send_file(result_file, as_attachment=True)
        with open(result_file, "r", encoding="utf-8") as file:
            content = file.read()
    else:
        content = constants.waiting_tip
    return render_template_string(
        "<head><link rel='icon' href='{{ url_for('static', filename='images/favicon.ico') }}' type='image/x-icon'></head><pre>{{ content }}</pre>",
        content=content,
    )


def remove_duplicates_from_tuple_list(tuple_list, seen, flag=None, force_str=None):
    """
    Remove duplicates from tuple list
    """
    unique_list = []
    for item in tuple_list:
        item_first = item[0]
        part = item_first
        if force_str:
            info = item_first.partition("$")[2]
            if info and info.startswith(force_str):
                continue
        if flag:
            matcher = re.search(flag, item_first)
            if matcher:
                part = matcher.group(1)
        if part not in seen:
            seen.add(part)
            unique_list.append(item)
    return unique_list


def process_nested_dict(data, seen, flag=None, force_str=None):
    """
    Process nested dict
    """
    for key, value in data.items():
        if isinstance(value, dict):
            process_nested_dict(value, seen, flag, force_str)
        elif isinstance(value, list):
            data[key] = remove_duplicates_from_tuple_list(value, seen, flag, force_str)


url_domain_pattern = re.compile(
    r"\b((https?):\/\/)?(\[[0-9a-fA-F:]+\]|([\w-]+\.)+[\w-]+)(:[0-9]{1,5})?\b"
)


def get_url_domain(url):
    """
    Get the url domain
    """
    matcher = url_domain_pattern.search(url)
    if matcher:
        return matcher.group()
    return None


def add_url_info(url, info):
    """
    Add url info to the URL
    """
    if info:
        separator = "-" if "$" in url else "$"
        url += f"{separator}{info}"
    return url


def format_url_with_cache(url, cache=None):
    """
    Format the URL with cache
    """
    cache = cache or get_url_domain(url) or ""
    return add_url_info(url, f"cache:{cache}") if cache else url


def remove_cache_info(str):
    """
    Remove the cache info from the string
    """
    return re.sub(r"[^a-zA-Z\u4e00-\u9fa5\$]?cache:.*", "", str)


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


def write_content_into_txt(content, path=None, newline=True, callback=None):
    """
    Write content into txt file
    """
    if not path:
        return

    with open(path, "a", encoding="utf-8") as f:
        if newline:
            f.write(f"\n{content}")
        else:
            f.write(content)

    if callback:
        callback()
