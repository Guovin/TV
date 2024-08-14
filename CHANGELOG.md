# 更新日志（Changelog）

## v1.3.5

### 2024/8/14

- 新增支持地区组播 ip 更新，调整默认以此模式运行，基本实现高清流畅播放（#225）（Added support for updating multicast IP for new regions and adjusted the default to run in this mode, basically achieving high-definition smooth playback (#225)）
- 新增支持使用 FFmpeg 进行测速排序、获取分辨率信息，本地运行请手动安装 FFmpeg（Added support for speed sorting and resolution information using FFmpeg. Manually install FFmpeg when running locally）
- 接口源增加分辨率信息，用于源切换时显示（Added resolution information to the interface source for display during source switching）
- 调整配置文件与结果文件路径（config、output 目录），方便 docker 卷挂载（#226）（Adjusted the paths for configuration and result files (config, output directories) to facilitate Docker volume mounting (#226)）
- 修改配置文件类型（config.ini）（Modified the configuration file type (config.ini)）

## v1.3.4

### 2024/7/31

- 新增配置 open_use_old_result：保留使用历史更新结果，合并至本次更新中（Add configuration open_use_old_result: Keep using the previous update results and merge them into the current update）
- 新增配置 open_keep_all：保留所有检索结果，推荐手动维护时开启（#121）（Add configuration open_keep_all: Keep all search results, recommend enabling it for manual maintenance (#121)）

## v1.3.3

### 2024/7/19

- 支持 Docker 卷挂载目录映射（Support for Docker volume mount directory mapping）
- 新增 requests 随机 User-Agent（Added random User-Agent for requests）
- 修复读取用户配置问题（#208）（Fixed issue with reading user configuration (#208)）
- 支持单日更新两次：6 点与 18 点（Supports updating twice a day: at 6 AM and 6 PM）

## v1.3.2

### 2024/7/10

- 新增支持频道名称简体繁体匹配（Added support for channel name Simplified and Traditional Chinese match）
- 新增 Docker 修改模板与配置教程（Added Docker modification template and configuration tutorial）
- 修复频道更新结果为空问题（Fixed the issue where channel update result is empty）

## v1.3.1

### 2024/7/9

- 重构代码，模块拆分，优化 CPU/内存占用（Refactor code, modular decomposition, optimize CPU/memory usage）
- 新增两种工作模式：driver 模式、requests 模式，具体差异见文档说明（Add two new working modes: driver mode and requests mode, see documentation for specific differences）
- 调整软件界面，功能分类摆放，增加配置：开启更新、开启浏览器模式、开启代理（Adjust the software interface, arrange features by category, add configurations: enable updates, enable browser mode, enable proxy）
- 调整工作流更新时间为北京时间每日 6:00（Adjust workflow update time to 6:00 AM Beijing time daily）
- Docker 镜像增加两种工作模式版本（Docker image adds two new working mode versions）

## v1.3.0

### 2024/7/1

- 新增更新结果页面服务（ip:8000）（Add new update results page service (ip:8000)）
- 新增支持 Docker 运行，并支持定时自动更新（Added support for Docker running and automatic updates）
- 修复在线查询更新，增加随机代理、失败重试，提高获取结果成功率（Fixed online query update, added random proxy, increased failure retry, and improved the success rate of getting results）
- 更换使用阿里云镜像源（Switched to use Alibaba Cloud mirror source）
- 增加更新开关配置：open_update（Add update switch configuration: open_update）
- 更新说明文档（Update documentation）

## v1.2.4

### 2024/6/21

- 优化排序执行逻辑（Optimize the sorting execution logic）
- 优化超时重试方法（Optimize the timeout retry method）
- 调整默认配置 open_sort：关闭工作流测速排序，建议本地运行更准确（Adjust the default configuration open_sort: turn off the workflow speed test sorting, local execution is recommended for more accurate results）

## v1.2.3

### 2024/6/17

- 新增请求重连重试功能（Added request reconnection retry function）
- 修复个别系统环境文件路径报错问题（Fixed some system environment file path errors）

## v1.2.2

### 2024/6/16

- 优化在线查询更新速度与修复无更新结果情况（Optimize online query update speed and fix no update result situation）
- 解决个别环境运行更新报错（Solved the problem of running updates in some environments）

## v1.2.1

### 2024/6/15

- 兼容 Win7 系统，请使用 Python 版本>=3.8（Compatible with Windows 7 system, please use Python version >= 3.8）
- 修复部分设备运行更新报错（Fixed an error that occurred when some devices ran updates）
- 修复工作流更新错误（Fixed an error in the workflow update）
- 新增捐赠途径（主页底部），本项目完全免费，维护不易，若对您有帮助，可选择捐赠（Add new donation channels (bottom of the homepage), this project is completely free, maintenance is not easy, if it helps you, you can choose to donate）

## v1.2.0

### 2024/6/9

- 异步并发、多线程支持，大幅提升更新速度（近 10 倍）（Asynchronous concurrency and multi-threading support, significantly increasing update speeds (nearly 10 times faster)）
- 新增更新工具软件（release 附件:update-tool.exe），首个版本可能会有不可预见的问题，请见谅（Added new update tool software (release attachment: update-tool.exe); the first version may have unforeseen issues, please be understanding）

## v1.1.6

### 2024/5/17

- 增加组播源可全地区运行更新（Added multicast sources to run region-wide updates）
- 修改默认值：关闭在线检索功能，组播源全地区更新（Change the default value: Disable the online search function and update the multicast source in all regions）

## v1.1.5

### 2024/5/17

- 增加模糊匹配规则，适配在线检索、订阅源、组播源（Add fuzzy matching rules for online search, subscription sources, and multicast sources）
- 增加订阅源、组播源更新进度条（Added the update progress bar for subscription sources and multicast sources）
- 优化组播源更新可能出现的无匹配结果情况（Optimize the possible situation of no match results in multicast source updates）
- 移除部分错误日志打印（Removes some error log prints）
- 移除严格匹配配置（Removes strict matching configurations）

## v1.1.4

### 2024/5/15

- 新增组播源功能（Added multicast source feature）
- 新增控制开关，控制多种获取模式的启用状态（Added control switch to manage the activation status of various acquisition modes）
- 新增严格匹配（Added strict matching）
- 优化文件读取，提升模板初始化速度（Optimized file reading to improve initialization speed based on templates）

## v1.1.3

### 2024/5/8

- 优化频道接口不对应问题（#99）（Optimize the mismatch problem of the channel interface (#99)）
- 处理 tqdm 安全问题（Handle the security issue of tqdm）
- 修改即将被废弃的命令（Modify the commands that are about to be deprecated）

## v1.1.2

### 2024/5/7

- 重构接口获取方法，增强通用性，适应结构变更（Refactored the method for obtaining the interface, enhanced its universality, and adapted to structural changes）
- 修复 gd 分支自动更新问题（#105）（Fixed the automatic update issue of the gd branch (#105)）
- 优化自定义接口源获取，接口去重（Optimized the acquisition of custom interface sources and removed duplicate interfaces）

## v1.1.1

### 2024/4/29

- 为避免代码合并冲突，移除 master 分支作为运行更新工作流，master 仅作为新功能发布分支，有使用我的链接的小伙伴请修改使用 gd 分支（void code merge conflicts, the master branch has been removed as the branch for running update workflows. The master branch is now only used for releasing new features. If you are using my link, please modify it to use the gd branch）

## v1.1.0

### 2024/4/26

- 新增自定义接口获取源，配置项为 extend_base_urls（#56）（Added custom interface for source acquisition, the configuration item is extend_base_urls (#56)）

## v1.0.9

### 2024/4/25

- 改进接口获取方法，增强处理多种失效场景（Improve the method of obtaining the interface, enhance the handling of various failure scenarios）

## v1.0.8

### 2024/4/24

- 跟进某个节点检索频道名称参数变更（#91）（Follow up on the parameter change of channel name retrieval for a certain node (#91)）
- 调整默认运行配置（Adjust the default running configuration）

## v1.0.7

### 2024/4/19

- 增加双节点接口来源，按最佳节点更新（Added dual-node interface source, update according to the best node）
- 优化频道更新结果为空的情况（#81）（Optimized the situation where the channel update result is empty (#81)）
- 调整工作流资源使用限制逻辑，在允许的范围内提升更新速度（Adjusted the logic of workflow resource usage limit, increase the update speed within the allowable range）

## v1.0.6

### 2024/4/12

- 恢复工作流更新，请谨慎合理使用，勿尝试更改默认运行参数，可能导致封禁的风险！首推使用本地更新（Workflow updates have been restored. Please use them carefully and do not attempt to change the default runtime parameters, as this may risk being banned! It is recommended to use local updates first.）
- 调整默认配置参数，降低单次更新运行时长（Adjusted the default configuration parameters to reduce the runtime of a single update.）
- 依赖版本锁定，解决可能出现的环境错误（#72）（Dependency versions have been locked to solve potential environmental errors (#72).）
- 优化逻辑与增加检测，避免网络异常占用工作流运行（Optimized logic and added checks to prevent network anomalies from occupying workflow operations.）

## v1.0.5

### 2024/4/10

- 移除工作流更新，鉴于有少数人反馈工作流甚至账号被封禁的情况，安全起见，只能暂时移除工作流更新机制，后续将增加其它平台部署方案（Removed workflow updates, in view of the feedback from a few people that their workflows and even accounts have been banned, for safety reasons, the workflow update mechanism can only be temporarily removed, and other platform deployment plans will be added in the future）
- 新增本地更新，同时移除更新频道个数限制，具体使用方法请见快速上手（Added local updates and removed the limit on the number of channel updates. For specific usage, please see the quick start guide）
- 适配提供方接口位置变更（Adapted to the change of the provider's interface location）

## v1.0.4

### 2024/4/8

- 更新 Github 使用条款，请务必仔细阅读并遵守（Updated GitHub Terms of Service, please read and comply carefully）
- 更新使用说明，关于可能导致工作流资源滥用的情况说明（Updated usage instructions, explanation about situations that may lead to workflow resource abuse）
- 增加.gitignore 文件，忽略用户配置、接口更新结果、日志文件等上传，非代码逻辑修改请不要发起 Pull requests，避免影响他人使用（Added .gitignore file to ignore uploads of user configurations, interface update results, log files, etc. Please do not initiate pull requests for non-code logic modifications to avoid affecting others' use）
- 调整更新频率，北京时间每日 8:00 执行一次（Adjusted update frequency, executes once daily at 8:00 am Beijing time）
- 调整更新频道数量上限（200 个）（Adjusted the maximum limit for updating channel numbers (200)）

## v1.0.3

### 2024/4/7

- 新增接口域名黑名单（Add interface domain blacklist）
- 新增接口关键字黑名单（Add interface keyword blacklist）
- 调整过滤逻辑执行顺序，提升工作流更新效率（Adjust the execution order of the filtering logic to improve workflow update efficiency）

## v1.0.2

### 2024/4/5

- 修复用户配置后接口更新结果与日志文件命名问题（Fix the issue of interface update results and log file naming after user configuration）

## v1.0.1

### 2024/4/1

- 适配接口提供方变更，调整接口链接与信息提取方法（Adapt to changes from the interface provider, adjust the interface link and information extraction method）

---

## v1.0.0

### 2024/3/30

- 修复工作流读取配置与更新文件对比问题（Fix the issue of workflow reading configuration and comparing updated files）

---

### 2024/3/29

- 修复用户专属配置更新结果失败（Fix user specific configuration update failure）

---

### 2024/3/26

- 新增快速上手-详细教程（Add a Quick Start - detailed tutorial）
- 新增以 releases 发布版本更新信息（Add release notes for version updates using releases）

---

### 2024/3/25

- 增加代码防覆盖，用户可使用 user\_作为文件前缀以区分独有配置，可避免在合并更新时本地代码被上游仓库代码覆盖，如 user_config.py、user_demo.txt、user_result.txt（Add code anti-overwriting. Users can use user\_ as the file prefix to distinguish unique configurations. This prevents local codes from being overwritten by upstream repository codes, such as user_config.py, user_demo.txt, and user_result.txt, when merging updates）

---

### 2024/3/21

- 修复潜在的更新文件追踪失效，导致更新失败（Fixed potential tracking failure of updated files, leading to update failure）
- 调整最近更新获取时间默认为 30 天（Adjusted the default recent update retrieval time to 30 days）
- 优化最近更新接口筛选，当筛选后不足指定接口个数时，将使用其它时间范围的可用接口补充（Optimized the recent update interface filter, when the number of interfaces is insufficient after filtering, other time range available interfaces will be used for supplementation）
- 优化珠江、CCTV 频道匹配问题（Optimized the matching problem of Zhujiang and CCTV channels）
- 移除推送实时触发更新（Removed push real-time trigger update）

---

### 2024/3/18

- 新增配置项：ipv_type，用于过滤 ipv4、ipv6 接口类型（Added configuration item: ipv_type, used to filter ipv4, ipv6 interface types）
- 优化文件更新逻辑，避免更新失效引起文件丢失（Optimized file update logic to prevent file loss caused by update failure）
- 调整分页获取默认值：关注频道获取 6 页，常规频道获取 4 页，以提升更新速度（Adjusted the default value for pagination: fetch 6 pages for followed channels, 4 pages for regular channels, to improve update speed）
- 增加接口日志文件 result.log 输出（Added output of interface log file result.log）
- 修复权重排序异常（Fixed weight sorting anomaly）

---

### 2024/3/15

- 优化代码结构（Optimize code structure）
- 新增接口日志，记录详细质量指标（Added interface logs to record detailed quality indicators）
- 新增可手动运行工作流触发更新（Added manual workflows to trigger updates）

---

### 2024/3/13

- 增加配置项：recent_days，筛选获取最近时间范围内更新的接口，默认最近 60 天（Added configuration item: recent_days, a filter to get the most recently updated interfaces, default to the last 60 days）
- 调整默认值：关注频道获取 8 页，常规频道获取 5 页（Adjusted default values: fetch 8 pages for followed channels, 5 pages for regular channels）

---

### 2024/3/6

- 更新文件代理说明（Update file proxy description）

---

### 2024/3/4

- 增加配置项：响应时间与分辨率权重值（Added configuration items: response time and resolution weight values）
- 移除配置项：是否过滤无效接口，始终执行过滤（Removed configuration items: whether to filter invalid interfaces, always perform filtering）
- 移除按日期排序，采用响应时间与分辨率作为排序规则（Removed sorting by date, using response time and resolution as sorting rules）
- 更新 README：增加修改更新频率、文件代理说明、更新日志（Updated README: added modification update frequency, file proxy description, update log）
