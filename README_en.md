# Television channel menu customization and live source interface update tool

Customize channel menus and automatically obtain and update the latest live source interfaces based on template files, verify, and generate usable channel interface files.

<p align="center">
  <a href="https://github.com/Guovin/TV/releases">
    <img src="https://img.shields.io/badge/Version-1.3.1-307cf7" />
  </a>
  <a>
    <img src="https://img.shields.io/badge/Python-%20%3E%3D%203.8-47c219" />
  </a>
  <a href="https://github.com/Guovin/TV/releases">
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
- Scheduled execution at 6:00 AM Beijing time daily
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

- requests: Lightweight, low performance requirements, fast update speed, stability uncertain (recommend this version only for subscription sources)
- driver: Higher performance requirements, slower update speed, high stability, high success rate (use this version for online search, multicast sources)

```bash
1. Pull the image:

For requests version:
docker pull guovern/tv-requests:latest

For driver version:
docker pull guovern/tv-driver:latest

2. Run the container: docker run --name tv-requests or driver -d -p 8000:8000 guovern/tv-requests or driver

3. Check the update results: Visit (domain:8000)

4. Customization (optional):

- Modify the template:
docker cp your_system_path/user-demo.txt tv-requests or driver:/app/user-demo.txt

- Modify the configuration:
docker cp your_system_path/user-config.py tv-requests or driver:/app/user-config.py
```

#### Note: Link to the result file after updates of methods one to three: http://local ip:8000

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
