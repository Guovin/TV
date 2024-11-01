from utils.config import config
import re
import os


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


open_update = config.getboolean("Settings", "open_update", fallback=True)

open_filter_resolution = config.getboolean(
    "Settings", "open_filter_resolution", fallback=True
)

ipv_type = config.get("Settings", "ipv_type", fallback="全部").lower()

ipv_type_prefer = [
    type.strip().lower()
    for type in config.get("Settings", "ipv_type_prefer", fallback="ipv4").split(",")
]

ipv4_num = config.getint("Settings", "ipv4_num", fallback=15)

ipv6_num = config.getint("Settings", "ipv6_num", fallback=15)

ipv_limit = {
    "ipv4": ipv4_num,
    "ipv6": ipv6_num,
}

origin_type_prefer = [
    origin.strip().lower()
    for origin in config.get(
        "Settings",
        "origin_type_prefer",
        fallback="subscribe,hotel,multicast,online_search",
    ).split(",")
    if origin.strip().lower()
]

hotel_num = config.getint("Settings", "hotel_num", fallback=10)

multicast_num = config.getint("Settings", "multicast_num", fallback=10)

subscribe_num = config.getint("Settings", "subscribe_num", fallback=10)

online_search_num = config.getint("Settings", "online_search_num", fallback=10)

source_limits = {
    "hotel": hotel_num,
    "multicast": multicast_num,
    "subscribe": subscribe_num,
    "online_search": online_search_num,
}

min_resolution = config.get("Settings", "min_resolution", fallback="1920x1080")

min_resolution_value = get_resolution_value(
    config.get("Settings", "min_resolution", fallback="1920x1080")
)

urls_limit = config.getint("Settings", "urls_limit", fallback=30)

open_url_info = config.getboolean("Settings", "open_url_info", fallback=True)

recent_days = config.getint("Settings", "recent_days", fallback=30)

domain_blacklist = [
    domain.strip()
    for domain in config.get("Settings", "domain_blacklist", fallback="").split(",")
    if domain.strip()
]

url_keywords_blacklist = [
    keyword.strip()
    for keyword in config.get("Settings", "url_keywords_blacklist", fallback="").split(
        ","
    )
    if keyword.strip()
]

source_file = config.get("Settings", "source_file", fallback="config/demo.txt")

final_file = config.get("Settings", "final_file", fallback="output/result.txt")

open_m3u_result = config.getboolean("Settings", "open_m3u_result", fallback=True)

open_keep_all = config.getboolean("Settings", "open_keep_all", fallback=False)

open_subscribe = config.getboolean("Settings", f"open_subscribe", fallback=True)

open_hotel = config.getboolean("Settings", f"open_hotel", fallback=True)

open_hotel_fofa = config.getboolean("Settings", f"open_hotel_fofa", fallback=True)

open_hotel_tonkiang = config.getboolean(
    "Settings", f"open_hotel_tonkiang", fallback=True
)

open_multicast = config.getboolean("Settings", f"open_multicast", fallback=True)

open_multicast_tonkiang = config.getboolean(
    "Settings", "open_multicast_tonkiang", fallback=True
)

open_multicast_fofa = config.getboolean(
    "Settings", "open_multicast_fofa", fallback=True
)

open_online_search = config.getboolean("Settings", f"open_online_search", fallback=True)

open_method = {
    "subscribe": open_subscribe,
    "hotel": open_hotel,
    "multicast": open_multicast,
    "online_search": open_online_search,
    "hotel_fofa": open_hotel_fofa,
    "hotel_tonkiang": open_hotel_tonkiang,
    "multicast_fofa": open_multicast_fofa,
    "multicast_tonkiang": open_multicast_tonkiang,
}

open_use_old_result = config.getboolean(
    "Settings", "open_use_old_result", fallback=True
)

open_sort = config.getboolean("Settings", "open_sort", fallback=True)

open_ffmpeg = config.getboolean("Settings", "open_ffmpeg", fallback=True)

ipv_type = config.get("Settings", "ipv_type", fallback="全部").lower()

open_update_time = config.getboolean("Settings", "open_update_time", fallback=True)

multicast_region_list = [
    region.strip()
    for region in config.get(
        "Settings", "multicast_region_list", fallback="全部"
    ).split(",")
    if region.strip()
]

hotel_region_list = [
    region.strip()
    for region in config.get("Settings", "hotel_region_list", fallback="全部").split(
        ","
    )
    if region.strip()
]

request_timeout = config.getint("Settings", "request_timeout", fallback=10)

sort_timeout = config.getint("Settings", "sort_timeout", fallback=10)

open_proxy = config.getboolean("Settings", "open_proxy", fallback=False)

open_driver = config.getboolean("Settings", "open_driver", fallback=True)

hotel_page_num = config.getint("Settings", "hotel_page_num", fallback=1)

multicast_page_num = config.getint("Settings", "multicast_page_num", fallback=1)

online_search_page_num = config.getint("Settings", "online_search_page_num", fallback=1)

subscribe_urls = [
    url.strip()
    for url in config.get("Settings", "subscribe_urls", fallback="").split(",")
    if url.strip()
]

response_time_weight = config.getfloat("Settings", "response_time_weight", fallback=0.5)

resolution_weight = config.getfloat("Settings", "resolution_weight", fallback=0.5)

open_update_time = config.getboolean("Settings", "open_update_time", fallback=True)

open_url_info = config.getboolean("Settings", "open_url_info", fallback=True)

log_dir = "output"

log_file = "result_new.log"

log_path = os.path.join(log_dir, log_file)

url_pattern = r"((https?):\/\/)?(\[[0-9a-fA-F:]+\]|([\w-]+\.)+[\w-]+)(:[0-9]{1,5})?(\/[^\s]*)?(\$[^\s]+)?"

rtp_pattern = r"^([^,，]+)(?:[,，])?(rtp://.*)$"

demo_txt_pattern = r"^([^,，]+)(?:[,，])?(?!#genre#)" + r"(" + url_pattern + r")?"

txt_pattern = r"^([^,，]+)(?:[,，])(?!#genre#)" + r"(" + url_pattern + r")"

m3u_pattern = r"^#EXTINF:-1.*?(?:，|,)(.*?)\n" + r"(" + url_pattern + r")"

sub_pattern = r"-|_|\((.*?)\)|\（(.*?)\）|\[(.*?)\]|\「(.*?)\」| |｜|频道|普清|标清|高清|HD|hd|超清|超高|超高清|中央|央视|台|电信|联通|移动"

replace_dict = {
    "plus": "+",
    "PLUS": "+",
    "＋": "+",
    "CCTV1综合": "CCTV1",
    "CCTV2财经": "CCTV2",
    "CCTV3综艺": "CCTV3",
    "CCTV4国际": "CCTV4",
    "CCTV4中文国际": "CCTV4",
    "CCTV4欧洲": "CCTV4",
    "CCTV5体育": "CCTV5",
    "CCTV5+体育赛视": "CCTV5+",
    "CCTV5+体育赛事": "CCTV5+",
    "CCTV5+体育": "CCTV5+",
    "CCTV6电影": "CCTV6",
    "CCTV7军事": "CCTV7",
    "CCTV7军农": "CCTV7",
    "CCTV7农业": "CCTV7",
    "CCTV7国防军事": "CCTV7",
    "CCTV8电视剧": "CCTV8",
    "CCTV9记录": "CCTV9",
    "CCTV9纪录": "CCTV9",
    "CCTV10科教": "CCTV10",
    "CCTV11戏曲": "CCTV11",
    "CCTV12社会与法": "CCTV12",
    "CCTV13新闻": "CCTV13",
    "CCTV新闻": "CCTV13",
    "CCTV14少儿": "CCTV14",
    "CCTV15音乐": "CCTV15",
    "CCTV16奥林匹克": "CCTV16",
    "CCTV17农业农村": "CCTV17",
    "CCTV17农业": "CCTV17",
}
