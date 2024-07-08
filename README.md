# TVBox 电视频道菜单自定义与直播源接口自动校验与更新工具

自定义频道菜单，根据模板文件的直播源接口，自动获取并更新最新的直播源接口，校验并生成可用的频道接口文件

[English](./README_en.md) | 中文

## 特点

- 自定义模板，生成您想要的频道分类与频道顺序
- 支持多种获取源方式：线上检索、组播源、酒店源、订阅源
- 接口测速验效，响应时间、分辨率优先级，过滤无效接口
- 定时执行，北京时间每日 6:00 执行更新
- 支持多种运行方式：工作流、命令行、界面软件、Docker
- 更多功能请见[配置参数](./docs/config.md)

## 配置

[配置参数](./docs/config.md)

## 快速上手

### 方式一：命令行更新

```python
pip3 install pipenv
pipenv install
pipenv run build
```

### 方式二：界面软件更新

1. 下载[更新工具软件](https://github.com/Guovin/TV/releases)，打开软件，点击更新，即可完成更新

2. 或者在项目目录下运行以下命令，即可打开界面软件：

```python
pipenv run ui
```

### 方式三：Docker 更新

```bash
1. 拉取镜像：docker pull guovern/tv:latest
2. 运行容器：docker run -d -p 8000:8000 tv
3. 访问（域名:8000）查看更新结果
```

#### 注：方式一至三更新完成后的结果文件链接：http://本地 ip:8000

### 方式四：工作流更新

Fork 本项目并开启工作流更新

[更多详细教程](./docs/tutorial.md)

如果您不想折腾，刚好我的配置符合您的需求，可以使用以下链接：

- 接口源：https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/result.txt
- 数据源：https://ghproxy.net/raw.githubusercontent.com/Guovin/TV/gd/source.json

## 更新日志

[更新日志](./CHANGELOG.md)

## 许可证

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)

## 赞赏

![image](./docs/images/appreciate.jpg)
