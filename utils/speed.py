from aiohttp import ClientSession, TCPConnector
from time import time
import asyncio
import re
from urllib.parse import quote
from utils.config import config
import subprocess

timeout = 15


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


async def ffmpeg_url(url):
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
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout + 15)
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
            url_info[0] = url_info[0] + f"${resolution}"
        url_info[2] = resolution
        return (tuple(url_info), frame)
    except Exception as e:
        print(e)
        return float("inf")


speed_cache = {}


async def get_speed_by_info(url_info, ffmpeg, semaphore, callback=None):
    """
    Get the info with speed
    """
    async with semaphore:
        url, _, _ = url_info
        url_info = list(url_info)
        cache_key = None
        if "$" in url:
            url, cache_info = url.split("$", 1)
            if "cache:" in cache_info:
                cache_key = cache_info.replace("cache:", "")
                if cache_key in speed_cache:
                    return tuple(url_info), speed_cache[cache_key]
        url = quote(url, safe=":/?&=$[]")
        url_info[0] = url
        try:
            if ".m3u8" not in url and ffmpeg:
                speed = await check_stream_speed(url_info)
                url_speed = speed[1] if speed != float("inf") else float("inf")
            else:
                url_speed = await get_speed(url)
                speed = (
                    (tuple(url_info), url_speed)
                    if url_speed != float("inf")
                    else float("inf")
                )
            if cache_key and cache_key not in speed_cache:
                speed_cache[cache_key] = url_speed
            return speed
        except Exception:
            return float("inf")
        finally:
            if callback and (cache_key is None or cache_key not in speed_cache):
                callback()


async def sort_urls_by_speed_and_resolution(data, ffmpeg=False, callback=None):
    """
    Sort by speed and resolution
    """
    semaphore = asyncio.Semaphore(10)
    response = await asyncio.gather(
        *(
            get_speed_by_info(url_info, ffmpeg, semaphore, callback=callback)
            for url_info in data
        )
    )
    valid_response = [res for res in response if res != float("inf")]

    def extract_resolution(resolution_str):
        numbers = re.findall(r"\d+x\d+", resolution_str)
        if numbers:
            width, height = map(int, numbers[0].split("x"))
            return width * height
        else:
            return 0

    default_response_time_weight = 0.5
    default_resolution_weight = 0.5
    response_time_weight = (
        config.getfloat("Settings", "response_time_weight")
        or default_response_time_weight
    )
    resolution_weight = (
        config.getfloat("Settings", "resolution_weight") or default_resolution_weight
    )
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

    sorted_res = sorted(valid_response, key=combined_key, reverse=True)
    return sorted_res
