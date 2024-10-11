<div align="center">
  <img src="./static/images/logo.png" alt="logo"/>
  <h1 align="center">电视直播源更新工具</h1>
</div>

<div align="center">自定义频道菜单，根据模板频道，自动获取并更新最新的直播源接口，测速校验后生成可用的接口文件</div>
<div align="center">默认结果包含：📺央视频道、💰央视付费频道、📡卫视频道、🏠广东频道、🌊港·澳·台频道、🎬电影频道、🎥咪咕直播</div>

<details>
  <summary>具体频道</summary>
  <div>
  📺央视频道：CCTV-1，CCTV-2，CCTV-3，CCTV-4，CCTV-5，CCTV-5+，CCTV-6，CCTV-7，CCTV-8，CCTV-9，CCTV-10，CCTV-11，CCTV-12，CCTV-13，CCTV-14，CCTV-15，CCTV-16，CCTV-17，CETV1，CETV2，CETV4，CETV5
  </div>
  <div>
  💰央视付费频道：文化精品，央视台球，风云音乐，第一剧场，风云剧场，怀旧剧场，女性时尚，高尔夫网球，风云足球，电视指南，世界地理，兵器科技
  </div>
  <div>
  📡卫视频道：广东卫视，香港卫视，浙江卫视，湖南卫视，北京卫视，湖北卫视，黑龙江卫视，安徽卫视，重庆卫视，东方卫视，东南卫视，甘肃卫视，广西卫视，贵州卫视，海南卫视，河北卫视，河南卫视，吉林卫视，江苏卫视，江西卫视，辽宁卫视，内蒙古卫视，宁夏卫视，青海卫视，山东卫视，山西卫视，陕西卫视，四川卫视，深圳卫视，三沙卫视，天津卫视，西藏卫视，新疆卫视，云南卫视
  </div>
  <div>
  🏠广东频道：广东珠江，广东体育，广东新闻，广东卫视，大湾区卫视，广州影视，广州竞赛，江门综合，江门侨乡生活，佛山综合，深圳卫视，汕头综合，汕头经济，汕头文旅，茂名综合，茂名公共
  </div>
  <div>
  🌊港·澳·台：翡翠台，明珠台，凤凰中文，凤凰资讯，凤凰香港，凤凰卫视，TVBS亚洲，香港卫视，纬来体育，纬来育乐，J2，Viutv，三立台湾，无线新闻，三立新闻，东森综合，东森超视，东森电影，Now剧集，Now华剧，靖天资讯，星卫娱乐，卫视卡式
  </div>
  <div>
  🎬电影频道：CHC家庭影院，CHC动作电影，CHC高清电影，淘剧场，淘娱乐，淘电影，NewTV惊悚悬疑，NewTV动作电影，黑莓电影，纬来电影，靖天映画，靖天戏剧，星卫娱乐，艾尔达娱乐，经典电影，IPTV经典电影，天映经典，无线星河，星空卫视，私人影院，东森电影，龙祥电影，东森洋片，东森超视
  </div>
  <div>🎥咪咕直播：咪咕直播1-45</div>
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

[English](./README_en.md) | 中文

## 特点

- 自定义模板，生成您想要的频道分类与频道顺序
- 支持多种获取源方式：组播源、酒店源、订阅源、线上检索
- 接口测速验效，响应时间、分辨率优先级，过滤无效接口
- 定时执行，北京时间每日 6:00 与 18:00 执行更新
- 支持多种运行方式：工作流、命令行、界面软件、Docker
- 更多功能请见[配置参数](./docs/config.md)

## 最新结果：

- 接口源：

```bash
  https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/output/result.m3u
```

- 数据源：

```bash
  https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/source.json
```

## 配置

[配置参数](./docs/config.md)

## 快速上手

### 方式一：工作流更新

Fork 本项目并开启工作流更新，具体步骤请见[详细教程](./docs/tutorial.md)

### 方式二：命令行更新

```python
pip3 install pipenv
pipenv install
pipenv run build
```

### 方式三：界面软件更新

1. 下载[更新工具软件](https://github.com/Guovin/TV/releases)，打开软件，点击更新，即可完成更新

2. 或者在项目目录下运行以下命令，即可打开界面软件：

```python
pipenv run ui
```

<img src="./docs/images/ui.png" alt="更新工具软件" title="更新工具软件" style="height:600px" />

### 方式四：Docker 更新

- requests：轻量级，性能要求低，更新速度快，稳定性不确定（推荐订阅源使用此版本）
- driver：性能要求较高，更新速度较慢，稳定性、成功率高；修改配置 open_driver = False 可切换到 request 版本（推荐酒店源、组播源、在线搜索使用此版本）

建议都试用一次，选择自己合适的版本。

```bash
1. 拉取镜像：
requests：
docker pull guovern/tv-requests:latest

driver：
docker pull guovern/tv-driver:latest

2. 运行容器：
docker run -d -p 8000:8000 guovern/tv-requests 或 tv-driver

卷挂载参数（可选）：
实现宿主机文件与容器文件同步，修改模板、配置、获取更新结果文件可直接在宿主机文件夹下操作

配置文件：
-v 宿主机路径/config:/tv-requests/config 或 tv-driver/config

结果文件：
-v 宿主机路径/output:/tv-requests/output 或 tv-driver/output

例：docker run -v /etc/docker/config:/tv-requests/config -v /etc/docker/output:/tv-requests/output -d -p 8000:8000 guovern/tv-requests

3. 查看更新结果：访问（域名:8000）
```

#### 注：方式一至三更新完成后的结果文件链接：http://本地 ip:8000 或 http://localhost:8000

## 更新日志

[更新日志](./CHANGELOG.md)

## 许可证

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)

## 赞赏

<div>如果对您有帮助，请赞赏，您的赞赏是我更新的动力~</div>
<img src="./static/images/appreciate.jpg" alt="赞赏码" title="赞赏码" style="height:350px" />
