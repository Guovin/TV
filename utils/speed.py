from aiohttp import ClientSession, TCPConnector
from time import time
import asyncio
import re
from utils.config import config
from utils.tools import is_ipv6, add_url_info, remove_cache_info, get_resolution_value
import subprocess
import yt_dlp


def get_speed_yt_dlp(url, timeout=config.sort_timeout):
    """
    Get the speed of the url by yt_dlp
    """
    try:
        ydl_opts = {
            "socket_timeout": timeout,
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            start = time()
            info = ydl.extract_info(url, download=False)
            return int(round((time() - start) * 1000)) if info else float("inf")
    except Exception as e:
        return float("inf")


async def get_speed(url, timeout=config.sort_timeout, proxy=None):
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
        return (url_info, frame)
    except Exception as e:
        print(e)
        return float("inf")


speed_cache = {}


def get_speed_by_info(url_info, ipv6_proxy=None, callback=None):
    """
    Get the info with speed
    """
    url, _, resolution, _ = url_info
    url_info = list(url_info)
    cache_key = None
    url_is_ipv6 = is_ipv6(url)
    if "$" in url:
        url, _, cache_info = url.partition("$")
        matcher = re.search(r"cache:(.*)", cache_info)
        if matcher:
            cache_key = matcher.group(1)
        url_show_info = remove_cache_info(cache_info)
    url_info[0] = url
    if cache_key in speed_cache:
        speed = speed_cache[cache_key][0]
        url_info[2] = speed_cache[cache_key][1]
        if speed != float("inf"):
            if url_show_info:
                url_info[0] = add_url_info(url, url_show_info)
            return (tuple(url_info), speed)
        else:
            return float("inf")
    try:
        if ipv6_proxy and url_is_ipv6:
            url_speed = 0
            speed = (url_info, url_speed)
        else:
            url_speed = get_speed_yt_dlp(url)
            speed = (url_info, url_speed) if url_speed != float("inf") else float("inf")
        if cache_key and cache_key not in speed_cache:
            speed_cache[cache_key] = (url_speed, resolution)
        if url_show_info:
            speed[0][0] = add_url_info(speed[0][0], url_show_info)
        speed = (tuple(speed[0]), speed[1])
        return speed
    except:
        return float("inf")
    finally:
        if callback:
            callback()


def sort_urls_by_speed_and_resolution(data, ipv6_proxy=None, callback=None):
    """
    Sort by speed and resolution
    """
    response = []
    for url_info in data:
        response.append(
            get_speed_by_info(url_info, ipv6_proxy=ipv6_proxy, callback=callback)
        )
    valid_response = [res for res in response if res != float("inf")]

    def combined_key(item):
        (_, _, resolution, _), response_time = item
        resolution_value = get_resolution_value(resolution) if resolution else 0
        return (
            -(config.response_time_weight * response_time)
            + config.resolution_weight * resolution_value
        )

    sorted_res = sorted(valid_response, key=combined_key, reverse=True)
    return sorted_res
