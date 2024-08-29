import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from updates.subscribe import get_channels_by_subscribe_urls
from driver.utils import get_soup_driver
from utils.config import config, resource_path
import json
import asyncio


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
    region_list = config.get("Settings", "multicast_region_list").split(",")
    urls_info = []
    with open(
        resource_path("updates/multicast/multicast_map.json"), "r", encoding="utf-8"
    ) as f:
        region_url = json.load(f)
    if "all" in region_list or "全部" in region_list:
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
        multicast_region_urls_info, multicast=True
    )
    with open(
        resource_path("updates/multicast/multicast_region_result.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(multicast_result, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    get_region_urls_from_IPTV_Multicast_source()
    asyncio.run(get_multicast_region_result())
