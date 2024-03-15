import aiohttp
import asyncio
import config
import time
import re
import datetime
import os


def getChannelItems():
    """
    Get the channel items from the source file
    """
    # Open the source file and read all lines.
    with open(config.source_file, "r") as f:
        lines = f.readlines()

    # Create a dictionary to store the channels.
    channels = {}
    current_channel = ""
    pattern = r"^(.*?),(?!#genre#)(.*?)$"

    for line in lines:
        line = line.strip()
        if "#genre#" in line:
            # This is a new channel, create a new key in the dictionary.
            current_channel = line.split(",")[0]
            channels[current_channel] = {}
        else:
            # This is a url, add it to the list of urls for the current channel.
            match = re.search(pattern, line)
            if match:
                if match.group(1) not in channels[current_channel]:
                    channels[current_channel][match.group(1)] = [match.group(2)]
                else:
                    channels[current_channel][match.group(1)].append(match.group(2))
    return channels


def removeFile():
    """
    Remove the old final file
    """
    if os.path.exists(config.final_file):
        os.remove(config.final_file)


def outputTxt(cate, channelUrls):
    """
    Update the final file
    """
    with open(config.final_file, "a") as f:
        f.write(cate + ",#genre#\n")
        for name, urls in channelUrls.items():
            for url in urls:
                if url is not None:
                    f.write(name + "," + url + "\n")
        f.write("\n")


def getUrlInfo(result):
    """
    Get the url, date and resolution
    """
    m3u8_div = result.find("div", class_="m3u8")
    url = m3u8_div.text.strip() if m3u8_div else None
    info_div = m3u8_div.find_next_sibling("div") if m3u8_div else None
    date = resolution = None
    if info_div:
        info_text = info_div.text.strip()
        date, resolution = (
            (info_text.partition(" ")[0] if info_text.partition(" ")[0] else None),
            (
                info_text.partition(" ")[2].partition("•")[2]
                if info_text.partition(" ")[2].partition("•")[2]
                else None
            ),
        )
    return url, date, resolution


async def getSpeed(url):
    """
    Get the speed of the url
    """
    async with aiohttp.ClientSession() as session:
        start = time.time()
        try:
            async with session.get(url, timeout=5) as response:
                resStatus = response.status
        except:
            return url, float("inf")
        end = time.time()
        if resStatus == 200:
            return url, end - start
        else:
            return url, float("inf")


async def compareSpeedAndResolution(infoList):
    """
    Sort by speed and resolution
    """
    response_times = await asyncio.gather(*(getSpeed(url) for url, _, _ in infoList))
    valid_responses = [
        (info, rt)
        for info, rt in zip(infoList, response_times)
        if rt[1] != float("inf")
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
            -(response_time_weight * response_time[1])
            + resolution_weight * resolution_value
        )

    sorted_res = sorted(valid_responses, key=combined_key)
    return sorted_res


def filterByDate(data):
    """
    Filter by date and limit
    """
    default_recent_days = 60
    use_recent_days = getattr(config, "recent_days", 60)
    if (
        not isinstance(use_recent_days, int)
        or use_recent_days <= 0
        or use_recent_days > 365
    ):
        use_recent_days = default_recent_days
    start_date = datetime.datetime.now() - datetime.timedelta(days=use_recent_days)
    recent_data = []
    for (url, date, resolution), response_time in data:
        if date:
            date = datetime.datetime.strptime(date, "%m-%d-%Y")
            if date >= start_date:
                recent_data.append(((url, date, resolution), response_time))
    return recent_data


def getTotalUrls(data):
    """
    Get the total urls with filter by date and limit
    """
    total_urls = []
    if len(data) > config.urls_limit:
        total_urls = [url for (url, _, _), _ in filterByDate(data)[: config.urls_limit]]
    else:
        total_urls = [url for (url, _, _), _ in data]
    return list(dict.fromkeys(total_urls))
