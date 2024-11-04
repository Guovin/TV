import os

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
