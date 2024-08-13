# Television channel menu customization and live source interface update tool

Customize channel menus and automatically obtain and update the latest live source interfaces based on template files, verify, and generate usable channel interface files.

<p align="center">
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
- Supports multiple source acquisition methods: online search, multicast source, hotel source, subscription source
- Interface speed testing and verification, with priority on response time and resolution, filtering out ineffective interfaces
- Scheduled execution at 6:00 AM and 18:00 PM Beijing time daily
- Supports various execution methods: workflows, command line, GUI software, Docker
- For more features, see [Config parameter](./docs/config_en.md)

## Config

[Config parameter](./docs/config_en.md)

## Quick Start

### Method 1: Command Line Update

```python
pip3 install pipenv
pipenv install
pipenv run build
```

### Method 2: GUI Software Update

1. Download [Update tool software](https://github.com/Guovin/TV/releases), open the software, click update to complete the update

2. Or run the following command in the project directory to open the GUI software:

```python
pipenv run ui
```

![Update tool software](./docs/images/ui.png 'Update tool software')

### Method 3: Docker Update

- requests: Lightweight, low performance requirements, fast update speed, stability uncertain (Recommend using this version for the multicast source and the subscription source)
- driver: Higher performance requirements, slower update speed, high stability, high success rate (Online search use this version)

It's recommended to try each one and choose the version that suits you. If you can get results with requests for online searches, prioritize choosing the version that uses requests.

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

3. Check the update results: Visit (domain:8000)
```

#### Note: Link to the result file after updates of methods one to three: http://local ip:8000 or http://localhost:8000

### Method 4: Workflow Update

Fork this project and enable workflow updates

[More detailed tutorial](./docs/tutorial_en.md)

If you don't want to bother, and my configuration just meets your needs, you can use the following links:

- Interface source: https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/result.txt
- Data source: https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/source.json

## Changelog

[Changelog](./CHANGELOG.md)

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)

## Appreciate

![image](./docs/images/appreciate.jpg)
