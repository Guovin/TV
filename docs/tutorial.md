# 使用教程

[English](./tutorial-EN.md) | 中文

## 步骤一：Fork 本项目

将本仓库的源代码复制至个人账号仓库中

### 1. 首页点击 Fork：

![Fork入口](./images/fork-btn.png 'Fork入口')

### 2. Fork 创建个人仓库：

![Fork详情](./images/fork-detail.png 'Fork详情')

1. 个人仓库命名，可按您喜欢的名字随意命名（最终直播源结果链接取决于该名称），这里以默认 TV 为例
2. 确认信息无误后，点击确认创建

## 步骤二：修改模板

当您在步骤一中点击确认创建，成功后会自动跳转到您的个人仓库。这个时候您的个人仓库就创建完成了，可以定制个人的直播源频道菜单了！

### 1. 点击 demo.txt 模板文件：

![demo.txt入口](./images/demo-btn.png 'demo.txt入口')

### 2. 创建个人模板 user_demo.txt：

![创建user_demo.txt](./images/edit-user-demo.png '创建user_demo.txt')

1. 创建文件
2. 模板文件命名为 user_demo.txt
3. 模板文件需要按照（频道分类,#genre#），（频道名称,频道接口）进行编写，注意是英文逗号。频道总数上限为 200 个，超出部分将无法更新。
4. 点击 Commit changes...进行保存

## 步骤三：修改配置

跟编辑模板一样，修改运行配置

### 1. 点击 config.py 配置文件：

![config.py入口](./images/config-btn.png 'config.py入口')

### 2. 复制默认配置文件内容：

![copy config.py](./images/copy-config.png '复制默认模板')

### 3. 新建个人配置文件 user_config.py：

![创建user_config.py](./images/edit-user-config.png '创建user_config.py')

1. 创建文件
2. 配置文件命名为 user_config.py
3. 粘贴默认模板，修改 source_file = "user_demo.txt"；final_file = "user_result.txt"
4. 点击 Commit changes...进行保存

按照您的需要适当调整配置，以下是默认配置说明
| 配置项 | 默认值 | 描述 |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| source_file | "demo.txt" | 模板文件名称 |
| final_file | "result.txt" | 生成文件名称 |
| favorite_list | ["广东珠江","CCTV-1","CCTV-5","CCTV-5+","CCTV-13","广东体育","广东卫视","大湾区卫视","浙江卫视","湖南卫视","翡翠台"] | 关注频道名称列表（仅用于与常规频道区分，自定义获取分页数量） |
| open_online_search | False | 开启线上检索源功能 |
| favorite_page_num | 5 | 关注频道获取分页数量 |
| default_page_num | 3 | 常规频道获取分页数量 |
| urls_limit | 10 | 单个频道接口数量 |
| open_sort | True | 开启排序功能（响应速度、日期、分辨率），若更执行时间较长可关闭此功能 |
| response_time_weight | 0.5 | 响应时间权重值（所有权重值总和应为 1） |
| resolution_weight | 0.5 | 分辨率权重值 （所有权重值总和应为 1） |
| recent_days | 30 | 获取最近时间范围内更新的接口（单位天），适当减小可避免出现匹配问题 |
| ipv_type | "ipv4" | 生成结果中接口的类型，可选值："ipv4"、"ipv6"、"all" |
| domain_blacklist | ["epg.pw"] | 接口域名黑名单，用于过滤低质量含广告类域名的接口 |
| url_keywords_blacklist | [] | 接口关键字黑名单，用于过滤含特定字符的接口 |
| open_subscribe | True | 开启订阅源功能 |
| subscribe_urls | ["https://m3u.ibert.me/txt/fmml_dv6.txt",<br>"https://m3u.ibert.me/txt/o_cn.txt",<br>"https://m3u.ibert.me/txt/j_iptv.txt"] | 订阅源列表 |
| open_multicast | True | 开启组播源功能 |
| region_list | ["all"] | 组播源地区列表，[更多地区](./fofa_map.py)，"all"表示所有地区 |

## 步骤四：本地运行更新（推荐，稳定，支持大量频道更新）

### 1. 安装 Python

请至官方下载并安装 Python，安装时请选择将 Python 添加到系统环境变量 Path 中

### 2. 运行更新

项目目录下打开终端 CMD 依次运行以下命令：

```python
pip3 install pipenv
pipenv install
pipenv run build
```

### 3. 更新文件至仓库

接口更新完成后，将 user_result.txt 上传至个人仓库，即可完成更新
![用户名与仓库名称](./images/rep-info.png '用户名与仓库名称')
https://mirror.ghproxy.com/raw.githubusercontent.com/您的github用户名/仓库名称（对应上述Fork创建时的TV）/master/user_result.txt

## 步骤五：更新源代码

由于本项目将持续迭代优化，如果您想获取最新的更新内容，可进行如下操作

### 1. Star

在我的仓库首页点击收藏该项目（您的 Star 是我持续更新的动力）
![Star](./images/star.png 'Star')

### 2. Watch

关注该项目，后续更新日志将以 releases 发布，届时您将收到邮件通知
![Watch-activity](./images/watch-activity.png 'Watch All Activity')

### 3. Sync fork

回到您的仓库首页，如果项目有更新内容，点击 Sync fork，Update branch 确认即可更新最新代码
![Sync-fork](./images/sync-fork.png 'Sync fork')

## 以下内容请谨慎使用，如果您有大量的频道需要更新，请使用本地更新，勿使用自动更新，配置不当可能导致账户或工作流封禁！

## 步骤六：开启自动更新（仅适合少量频道更新）

如果您的模板和配置修改没有问题的话，这时就可以配置 Actions 来实现自动更新啦

### 1. 进入 Actions：

![Actions入口](./images/actions-btn.png 'Actions入口')

### 2. 开启 Actions 工作流：

![开启Actions工作流](./images/actions-enable.png '开启Actions工作流')
由于 Fork 的仓库 Actions 工作流是默认关闭的，需要您手动确认开启，点击红框中的按钮确认开启

![Actions工作流开启成功](./images/actions-home.png 'Actions工作流开启成功')
开启成功后，可以看到目前是没有任何工作流在运行的，别急，下面开始运行您第一个更新工作流

### 3. 运行更新工作流：

#### （1）启用 update schedule：

![开启Workflows更新](./images/workflows-btn.png '开启Workflows更新')

1. 点击 Workflows 分类下的 update schedule
2. 由于 Fork 的仓库工作流是默认关闭的，点击 Enable workflow 按钮确认开启

#### （2）根据分支运行 Workflow：

![运行Workflow](./images/workflows-run.png '运行Workflow')
这个时候就可以运行更新工作流了

1. 点击 Run workflow
2. 这里可以切换您要运行的仓库分支，由于 Fork 默认拉取的是 master 分支，如果您修改的模板和配置也在 master 分支，这里选择 master 就好了，点击 Run workflow 确认运行

#### （3）Workflow 运行中：

![Workflow运行中](./images/workflow-running.png 'Workflow运行中')
稍等片刻，就可以看到您的第一条更新工作流已经在运行了！
（注意：由于运行时间取决于您的模板频道数量以及页数等配置，也很大程度取决于当前网络状况，请耐心等待，默认模板与配置一般需要 25 分钟左右。）

#### （4）Workflow 取消运行：

![取消运行Workflow](./images/workflow-cancel.png '取消运行Workflow')
如果您觉得这次的更新不太合适，需要修改模板或配置再运行，可以点击 Cancel run 取消本次运行

#### （5）Workflow 运行成功：

![Workflow执行成功](./images/workflow-success.png 'Workflow执行成功')
如果一切正常，稍等片刻后就可以看到该条工作流已经执行成功（绿色勾图标）。此时您可以访问代理文件链接，查看最新结果有没有同步即可：
![用户名与仓库名称](./images/rep-info.png '用户名与仓库名称')
https://mirror.ghproxy.com/raw.githubusercontent.com/您的github用户名/仓库名称（对应上述Fork创建时的TV）/master/user_result.txt

如果访问该链接能正常返回更新后的接口内容，说明您的直播源接口链接已经大功告成了！将该链接复制粘贴到 TVBox 等软件配置栏中即可使用~

- 注意：除了首次执行工作流需要您手动触发，后续执行（默认北京时间每日 8:00）将自动触发。如果您修改了模板或配置文件想立刻执行更新，可手动触发（2）中的 Run workflow 即可。

## 步骤七：修改工作流更新频率

![.github/workflows/main.yml](./images/schedule-cron.png '.github/workflows/main.yml')
如果您想修改更新频率（默认北京时间每日 8:00），可修改 on:schedule:- cron 字段。

### 1. 强烈不建议修改，因为短时间内的接口内容并无差异，过高的更新频率与高耗时运行的工作流都有可能被判定为资源滥用，导致仓库与账户被封禁的风险。

### 2. 请留意您的工作流运行时长，若发现执行时间过长，需要适当删减模板中频道数量、修改配置中的分页数量和接口数量，以达到合规的运行要求。
