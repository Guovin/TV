import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from updates.subscribe import get_channels_by_subscribe_urls
from driver.utils import get_soup_driver
from utils.config import resource_path, config
from utils.channel import format_channel_name
from utils.tools import get_pbar_remaining
import json

# import asyncio
from requests import Session
from collections import defaultdict
import re
from time import time
from tqdm import tqdm


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
    with open(
        resource_path("updates/multicast/multicast_map.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(region_url, f, ensure_ascii=False, indent=4)


def get_multicast_urls_info_from_region_list():
    """
    Get the multicast urls info from region
    """
    urls_info = []
    with open(
        resource_path("updates/multicast/multicast_map.json"), "r", encoding="utf-8"
    ) as f:
        region_url = json.load(f)
        urls_info = [
            {"region": region, "type": type, "url": url}
            for region, value in region_url.items()
            for type, url in value.items()
        ]
        return urls_info


async def get_multicast_region_result():
    """
    Get multicast region result
    """
    multicast_region_urls_info = get_multicast_urls_info_from_region_list()
    multicast_result = await get_channels_by_subscribe_urls(
        multicast_region_urls_info, multicast=True
    )
    with open(
        resource_path("updates/multicast/multicast_region_result.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(multicast_result, f, ensure_ascii=False, indent=4)


def get_multicast_region_type_result_txt():
    """
    Get multicast region type result txt
    """
    with open(
        resource_path("updates/multicast/multicast_map.json"), "r", encoding="utf-8"
    ) as f:
        region_url = json.load(f)
        session = Session()
        for region, value in region_url.items():
            for type, url in value.items():
                response = session.get(url)
                content = response.text
                with open(
                    resource_path(f"updates/multicast/rtp/{region}_{type}.txt"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(content)


def get_multicast_region_result_by_rtp_txt(callback=None):
    """
    Get multicast region result by rtp txt
    """
    rtp_file_list = []
    rtp_path = resource_path("updates/multicast/rtp")
    config_region_list = set(config.get("Settings", "multicast_region_list").split(","))
    for filename in os.listdir(rtp_path):
        if filename.endswith(".txt") and "_" in filename:
            name = filename.rsplit(".", 1)[0]
            if (
                name in config_region_list
                or "all" in config_region_list
                or "ALL" in config_region_list
                or "全部" in config_region_list
            ):
                rtp_file_list.append(filename)
    rtp_file_list_len = len(rtp_file_list)
    pbar = tqdm(total=rtp_file_list_len, desc="Loading local multicast rtp files")
    if callback:
        callback(
            f"正在加载本地组播数据, 共{rtp_file_list_len}个文件",
            0,
        )
    multicast_result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    pattern = re.compile(r"^(.*?),(?!#genre#)(.*?)$")
    start_time = time()
    for filename in rtp_file_list:
        region, type = filename.split("_")
        with open(os.path.join(rtp_path, filename), "r", encoding="utf-8") as f:
            for line in f:
                matcher = pattern.match(line)
                if matcher and len(matcher.groups()) == 2:
                    channel_name = format_channel_name(matcher.group(1).strip())
                    url = matcher.group(2).strip()
                    if url not in multicast_result[channel_name][region][type]:
                        multicast_result[channel_name][region][type].append(url)
            pbar.update()
            if callback:
                callback(
                    f"正在加载{region}_{type}的组播数据, 剩余{rtp_file_list_len - pbar.n}个文件, 预计剩余时间: {get_pbar_remaining(n=pbar.n, total=pbar.total, start_time=start_time)}",
                    int((pbar.n / rtp_file_list_len) * 100),
                )

    with open(
        resource_path("updates/multicast/multicast_region_result.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(multicast_result, f, ensure_ascii=False, indent=4)
    pbar.close()


if __name__ == "__main__":
    get_region_urls_from_IPTV_Multicast_source()
    # asyncio.run(get_multicast_region_result())
    get_multicast_region_type_result_txt()
    # get_multicast_region_result_by_rtp_txt()
