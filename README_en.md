# TVBox Custom TV Channel Menu and Live Source Interface Automatic Verification and Update Tool

Customize channel menus and automatically obtain and update the latest live source interfaces based on template files, verify, and generate usable channel interface files.

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

### Method 3: Docker Update

```bash
1. Pull the image: docker pull guovern/tv:latest
2. Run the container: docker run -d -p 8000:8000 tv
3. Access (domain:8000) to check the update results
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
