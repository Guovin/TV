import asyncio
import re
import subprocess
from time import time
from urllib.parse import quote

import m3u8
import yt_dlp
from aiohttp import ClientSession, TCPConnector

import utils.constants as constants
from utils.config import config
from utils.tools import is_ipv6, remove_cache_info, get_resolution_value, get_logger

logger = get_logger(constants.log_path)


async def get_speed_with_download(url, timeout=config.sort_timeout):
    """
    Get the speed of the url with a total timeout
    """
    start_time = time()
    total_size = 0
    total_time = 0
    try:
        async with ClientSession(
                connector=TCPConnector(ssl=False), trust_env=True
        ) as session:
            async with session.get(url, timeout=timeout) as response:
                async for chunk in response.content.iter_any():
                    if chunk:
                        total_size += len(chunk)
    except Exception as e:
        pass
    finally:
        end_time = time()
        total_time += end_time - start_time
    average_speed = (total_size / total_time if total_time > 0 else 0) / 1024
    return average_speed


async def get_speed_m3u8(url, timeout=config.sort_timeout):
    """
    Get the speed of the m3u8 url with a total timeout
    """
    start_time = time()
    total_size = 0
    total_time = 0
    try:
        url = quote(url, safe=':/?$&=@')
        m3u8_obj = m3u8.load(url)
        async with ClientSession(
                connector=TCPConnector(ssl=False), trust_env=True
        ) as session:
            for segment in m3u8_obj.segments:
                if time() - start_time > timeout:
                    break
                ts_url = segment.absolute_uri
                async with session.get(ts_url, timeout=timeout) as response:
                    file_size = 0
                    async for chunk in response.content.iter_any():
                        if chunk:
                            file_size += len(chunk)
                    end_time = time()
                    download_time = end_time - start_time
                    total_size += file_size
                    total_time += download_time
    except Exception as e:
        pass
    average_speed = (total_size / total_time if total_time > 0 else 0) / 1024
    return average_speed


def get_info_yt_dlp(url, timeout=config.sort_timeout):
    """
    Get the url info by yt_dlp
    """
    ydl_opts = {
        "socket_timeout": timeout,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "format": "best",
        "logger": logger,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.sanitize_info(ydl.extract_info(url, download=False))


async def get_speed_yt_dlp(url, timeout=config.sort_timeout):
    """
    Get the speed of the url by yt_dlp
    """
    try:
        start_time = time()
        info = await asyncio.wait_for(
            asyncio.to_thread(get_info_yt_dlp, url, timeout), timeout=timeout
        )
        fps = int(round((time() - start_time) * 1000)) if len(info) else float("inf")
        resolution = (
            f"{info['width']}x{info['height']}"
            if "width" in info and "height" in info
            else None
        )
        return fps, resolution
    except:
        return float("inf"), None


async def get_speed_requests(url, timeout=config.sort_timeout, proxy=None):
    """
    Get the speed of the url by requests
    """
    async with ClientSession(
            connector=TCPConnector(ssl=False), trust_env=True
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


async def ffmpeg_url(url, timeout=config.sort_timeout):
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
        url_info[2] = resolution
        return url_info, frame
    except Exception as e:
        print(e)
        return float("inf")


speed_cache = {}


async def get_speed(url, ipv6_proxy=None, callback=None):
    """
    Get the speed (response time and resolution) of the url
    """
    try:
        cache_key = None
        url_is_ipv6 = is_ipv6(url)
        if "$" in url:
            url, _, cache_info = url.partition("$")
            matcher = re.search(r"cache:(.*)", cache_info)
            if matcher:
                cache_key = matcher.group(1)
        if cache_key in speed_cache:
            return speed_cache[cache_key][0]
        if ipv6_proxy and url_is_ipv6:
            speed = (0, None)
        # elif '.m3u8' in url:
        #     speed = await get_speed_m3u8(url)
        else:
            speed = await get_speed_yt_dlp(url)
        if cache_key and cache_key not in speed_cache:
            speed_cache[cache_key] = speed
        return speed
    except:
        return float("inf"), None
    finally:
        if callback:
            callback()


def sort_urls_by_speed_and_resolution(name, data, logger=None):
    """
    Sort by speed and resolution
    """
    filter_data = []
    for url, date, resolution, origin in data:
        if origin == "important":
            filter_data.append((url, date, resolution, origin))
            continue
        cache_key_match = re.search(r"cache:(.*)", url.partition("$")[2])
        cache_key = cache_key_match.group(1) if cache_key_match else None
        if cache_key and cache_key in speed_cache:
            cache = speed_cache[cache_key]
            if cache:
                response_time, cache_resolution = cache
                resolution = cache_resolution or resolution
                if response_time != float("inf"):
                    url = remove_cache_info(url)
                    try:
                        if logger:
                            logger.info(
                                f"Name: {name}, URL: {url}, Date: {date}, Resolution: {resolution}, Response Time: {response_time} ms"
                            )
                    except Exception as e:
                        print(e)
                    filter_data.append((url, date, resolution, origin))

    def combined_key(item):
        _, _, resolution, origin = item
        if origin == "important":
            return -float("inf")
        else:
            resolution_value = get_resolution_value(resolution) if resolution else 0
            return (
                    config.response_time_weight * response_time
                    - config.resolution_weight * resolution_value
            )

    filter_data.sort(key=combined_key)
    return filter_data
