from aiohttp import ClientSession, TCPConnector
from time import time
import asyncio
import re
from utils.config import config
from utils.tools import is_ipv6, get_resolution_value
import subprocess

timeout = config.getint("Settings", "sort_timeout", fallback=5)


async def get_speed(url, timeout=timeout, proxy=None):
    """
    Get the speed of the url
    """
    async with ClientSession(
        connector=TCPConnector(verify_ssl=False), trust_env=True
    ) as session:
        start = time()
        end = None
        try:
            async with session.get(url, timeout=timeout, proxy=proxy) as response:
                if response.status == 404:
                    return float("inf")
                content = await response.read()
                if content:
                    end = time()
                else:
                    return float("inf")
        except Exception as e:
            return float("inf")
        return int(round((end - start) * 1000)) if end else float("inf")


def is_ffmpeg_installed():
    """
    Check ffmpeg is installed
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


async def ffmpeg_url(url, timeout=timeout):
    """
    Get url info by ffmpeg
    """
    args = ["ffmpeg", "-t", str(timeout), "-stats", "-i", url, "-f", "null", "-"]
    proc = None
    res = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout + 2)
        if out:
            res = out.decode("utf-8")
        if err:
            res = err.decode("utf-8")
        return None
    except asyncio.TimeoutError:
        if proc:
            proc.kill()
        return None
    except Exception:
        if proc:
            proc.kill()
        return None
    finally:
        if proc:
            await proc.wait()
        return res


def get_video_info(video_info):
    """
    Get the video info
    """
    frame_size = float("inf")
    resolution = None
    if video_info is not None:
        info_data = video_info.replace(" ", "")
        matches = re.findall(r"frame=(\d+)", info_data)
        if matches:
            frame_size = int(matches[-1])
        match = re.search(r"(\d{3,4}x\d{3,4})", video_info)
        if match:
            resolution = match.group(0)
    return frame_size, resolution


async def check_stream_speed(url_info):
    """
    Check the stream speed
    """
    try:
        url = url_info[0]
        video_info = await ffmpeg_url(url)
        if video_info is None:
            return float("inf")
        frame, resolution = get_video_info(video_info)
        if frame is None or frame == float("inf"):
            return float("inf")
        if resolution:
            url_info[0] = add_info_url(url, resolution)
        url_info[2] = resolution
        return (tuple(url_info), frame)
    except Exception as e:
        print(e)
        return float("inf")


def add_info_url(url, info):
    """
    Format the url
    """
    separator = "|" if "$" in url else "$"
    url += f"{separator}{info}"
    return url


speed_cache = {}


async def get_speed_by_info(
    url_info, ffmpeg, semaphore, ipv6_proxy=None, callback=None
):
    """
    Get the info with speed
    """
    async with semaphore:
        url, _, resolution, _ = url_info
        url_info = list(url_info)
        cache_key = None
        if "$" in url:
            url, cache_info = url.split("$", 1)
            if "cache:" in cache_info:
                matcher = re.search(r"cache:(.*)", cache_info)
                if matcher:
                    cache_key = matcher.group(1)
        url_is_ipv6 = is_ipv6(url)
        if url_is_ipv6:
            url = add_info_url(url, "IPv6")
        url_info[0] = url
        if cache_key in speed_cache:
            speed = speed_cache[cache_key][0]
            url_info[2] = speed_cache[cache_key][1]
            return (tuple(url_info), speed) if speed != float("inf") else float("inf")
        try:
            if ipv6_proxy and url_is_ipv6:
                url = ipv6_proxy + url
            if ffmpeg:
                speed = await check_stream_speed(url_info)
                url_speed = speed[1] if speed != float("inf") else float("inf")
                if url_speed == float("inf"):
                    url_speed = await get_speed(url)
                resolution = speed[0][2] if speed != float("inf") else None
            else:
                url_speed = await get_speed(url)
                speed = (
                    (tuple(url_info), url_speed)
                    if url_speed != float("inf")
                    else float("inf")
                )
            if cache_key and cache_key not in speed_cache:
                speed_cache[cache_key] = (url_speed, resolution)
            return speed
        except Exception:
            return float("inf")
        finally:
            if callback:
                callback()


response_time_weight = config.getfloat("Settings", "response_time_weight", fallback=0.5)
resolution_weight = config.getfloat("Settings", "resolution_weight", fallback=0.5)


async def sort_urls_by_speed_and_resolution(
    data, ffmpeg=False, ipv6_proxy=None, callback=None
):
    """
    Sort by speed and resolution
    """
    semaphore = asyncio.Semaphore(20)
    response = await asyncio.gather(
        *(
            get_speed_by_info(
                url_info, ffmpeg, semaphore, ipv6_proxy=ipv6_proxy, callback=callback
            )
            for url_info in data
        )
    )
    valid_response = [res for res in response if res != float("inf")]

    def combined_key(item):
        (_, _, resolution), response_time = item
        resolution_value = get_resolution_value(resolution) if resolution else 0
        return (
            -(response_time_weight * response_time)
            + resolution_weight * resolution_value
        )

    sorted_res = sorted(valid_response, key=combined_key, reverse=True)
    return sorted_res
