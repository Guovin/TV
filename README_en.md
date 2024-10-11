<div align="center">
  <img src="./static/images/logo.png" alt="logo"/>
  <h1 align="center">Live TV source update tool</h1>
</div>

<div align="justify">Customize the channel menu, automatically obtain and update the latest live source interfaces based on the template channels, and generate available interface files after speed test verification.</div>
<div align="justify">Default results include: 📺CCTV Channel, 💰CCTV Pay Channel, 📡Satellite TV Channel, 🏠Guangdong Channel, 🌊Hong Kong · Macao · Taiwan Channel, 🎬Movie Channel, 🎥Migu Live Streaming.</div>

<details>
  <summary>Specific channel</summary>
  <div>
  📺CCTV Channel：CCTV-1，CCTV-2，CCTV-3，CCTV-4，CCTV-5，CCTV-5+，CCTV-6，CCTV-7，CCTV-8，CCTV-9，CCTV-10，CCTV-11，CCTV-12，CCTV-13，CCTV-14，CCTV-15，CCTV-16，CCTV-17，CETV1，CETV2，CETV4，CETV5
  </div>
  <div>
  💰CCTV Pay Channel：文化精品，央视台球，风云音乐，第一剧场，风云剧场，怀旧剧场，女性时尚，高尔夫网球，风云足球，电视指南，世界地理，兵器科技
  </div>
  <div>
  📡Satellite TV Channel：广东卫视，香港卫视，浙江卫视，湖南卫视，北京卫视，湖北卫视，黑龙江卫视，安徽卫视，重庆卫视，东方卫视，东南卫视，甘肃卫视，广西卫视，贵州卫视，海南卫视，河北卫视，河南卫视，吉林卫视，江苏卫视，江西卫视，辽宁卫视，内蒙古卫视，宁夏卫视，青海卫视，山东卫视，山西卫视，陕西卫视，四川卫视，深圳卫视，三沙卫视，天津卫视，西藏卫视，新疆卫视，云南卫视
  </div>
  <div>
  🏠Guangdong Channel：广东珠江，广东体育，广东新闻，广东卫视，大湾区卫视，广州影视，广州竞赛，江门综合，江门侨乡生活，佛山综合，深圳卫视，汕头综合，汕头经济，汕头文旅，茂名综合，茂名公共
  </div>
  <div>
  🌊Hong Kong · Macao · Taiwan Channel：翡翠台，明珠台，凤凰中文，凤凰资讯，凤凰香港，凤凰卫视，TVBS亚洲，香港卫视，纬来体育，纬来育乐，J2，Viutv，三立台湾，无线新闻，三立新闻，东森综合，东森超视，东森电影，Now剧集，Now华剧，靖天资讯，星卫娱乐，卫视卡式
  </div>
  <div>
  🎬Movie Channel：CHC家庭影院，CHC动作电影，CHC高清电影，淘剧场，淘娱乐，淘电影，NewTV惊悚悬疑，NewTV动作电影，黑莓电影，纬来电影，靖天映画，靖天戏剧，星卫娱乐，艾尔达娱乐，经典电影，IPTV经典电影，天映经典，无线星河，星空卫视，私人影院，东森电影，龙祥电影，东森洋片，东森超视
  </div>
  <div>🎥Migu Live Streaming：咪咕直播1-45</div>
</details>

<p align="center" style="margin-top: 8px">
  <a href="https://github.com/Guovin/TV/releases/latest">
    <img src="https://img.shields.io/github/v/release/guovin/tv" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-%20%3E%3D%203.8-47c219" />
  </a>
  <a href="https://github.com/Guovin/TV/releases/latest">
    <img src="https://img.shields.io/github/downloads/guovin/tv/total" />
  </a>
  <a href="https://hub.docker.com/repository/docker/guovern/tv-requests">
    <img src="https://img.shields.io/docker/pulls/guovern/tv-requests?label=docker:requests" />
  </a>
   <a href="https://hub.docker.com/repository/docker/guovern/tv-driver">
    <img src="https://img.shields.io/docker/pulls/guovern/tv-driver?label=docker:driver" />
  </a>
</p>

[中文](./README.md) | English

## Features

- Custom templates for creating desired channel categories and order
- Supports multiple source acquisition methods: multicast source, hotel source, subscription source, online search
- Interface speed testing and verification, with priority on response time and resolution, filtering out ineffective interfaces
- Scheduled execution at 6:00 AM and 18:00 PM Beijing time daily
- Supports various execution methods: workflows, command line, GUI software, Docker
- For more features, see [Config parameter](./docs/config_en.md)

## Latest results：

- Interface source:

```bash
  https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/output/result.m3u
```

- Data source:

```bash
  https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/source.json
```

## Config

[Config parameter](./docs/config_en.md)

## Quick Start

### Method 1: Workflow Update

Fork this project and initiate workflow updates, detailed steps are available at [Detailed Tutorial](./docs/tutorial_en.md)

### Method 2: Command Line Update

```python
pip3 install pipenv
pipenv install
pipenv run build
```

### Method 3: GUI Software Update

1. Download [Update tool software](https://github.com/Guovin/TV/releases), open the software, click update to complete the update

2. Or run the following command in the project directory to open the GUI software:

```python
pipenv run ui
```

<img src="./docs/images/ui.png" alt="Update tool software" title="Update tool software" style="height:600px" />

### Method 4: Docker Update

- requests: Lightweight, low performance requirements, fast update speed, stability uncertain (recommend using this version for the subscription source)
- driver: Higher performance requirements, slower update speed, high stability and success rate. Set open_driver = False to switch to the request version (recommended for hotel sources, multicast sources, and online searches)

It's recommended to try each one and choose the version that suits you.

```bash
1. Pull the image:
For requests version:
docker pull guovern/tv-requests:latest

For driver version:
docker pull guovern/tv-driver:latest

2. Run the container:
docker run -d -p 8000:8000 guovern/tv-requests or driver

Volume Mount Parameter (Optional):
This allows synchronization of files between the host machine and the container. Modifying templates, configurations, and retrieving updated result files can be directly operated in the host machine's folder.

config:
-v <path>/config:/tv-requests/config or tv-driver/config

result:
-v <path>/output:/tv-requests/output or tv-driver/output

For example: docker run -v /etc/docker/config:/tv-requests/config -v /etc/docker/output:/tv-requests/output -d -p 8000:8000 guovern/tv-requests

3. Check the update results: Visit (domain:8000)
```

#### Note: Link to the result file after updates of methods one to three: http://local ip:8000 or http://localhost:8000

## Changelog

[Changelog](./CHANGELOG.md)

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)

## Appreciate

<div>If you find it helpful, please give a tip, your support is my motivation to update~</div>
<img src="./static/images/appreciate.jpg" alt="appreciate code" title="appreciate code" style="height:350px" />
