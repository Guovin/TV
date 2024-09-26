# 更新日志（Changelog）

## v1.4.7

### 2024/09/26

- 修复部分设备本地运行软件 driver 问题(#335)
- 修复 driver 模式下新版谷歌浏览器白屏问题
- 增加历史结果缓存(result_cache.pkl)，用于测速优化
- 重构测速方法，提升测速效率
- 优化测速进度条显示

- Fix some issues with local software driver operation on certain devices (#335)
- Fix the white screen issue with the new version of Google Chrome in driver mode
- Add historical result cache (result_cache.pkl) for performance optimization
- Refactor speed test methods to improve efficiency
- Optimize speed test progress bar display

## v1.4.6

### 2024/9/20

- 优化 IPv6 测试是否支持(#328)
- 优化 404 类接口测速(#329)

- Optimize IPv6 test support (#328)
- Optimize 404 class interface speed test (#329)

## v1.4.5

### 2024/9/19

- 修复 IPv6 接口测速(#325)

- Fix IPv6 Interface Speed Test (#325)

## v1.4.4

### 2024/9/14

- 修复组播接口测速可能出现结果频道分类空的问题
- 修复使用历史更新结果时可能出现模板不存在的频道问题
- 更新 FOFA 组播、酒店缓存
- 更新默认模板(demo.txt)内容
- 更新使用教程

- Fix the issue where multicast interface speed test may result in an empty channel category
- Fix the issue where channels may appear missing when updating results with history
- Update FOFA multicast and hotel cache
- Update default template (demo.txt) content
- Update user guide

## v1.4.3

### 2024/9/11

- 修正 RTP 文件：贵州电信文件错误，第一财经、东方财经等频道命名，地址错误

- Fixed RTP files: Corrected errors in Guizhou Telecom files, including naming and address errors for channels such as First Financial and Oriental Financial

## v1.4.2

### 2024/9/10

- 新增内蒙古、甘肃、海南、云南地区
- 更新 FOFA 酒店、组播缓存
- 更新组播 RTP 文件
- 优化测速过滤无效接口
- 增加接口域名黑名单，避免频道花屏情况
- 修复 FOFA requests 模式请求失败导致程序中止问题

- Added Inner Mongolia, Gansu, Hainan, and Yunnan regions
- Updated FOFA hotels and multicast cache
- Updated multicast RTP files
- Optimize speed test to filter out invalid interfaces
- Add interface domain name blacklist to avoid channel screen distortion
- Fix issue where FOFA requests mode failure leads to program termination

## v1.4.1

### 2024/9/9

- 新增 FOFA 缓存，解决访问限制问题
- 修复 CCTV-5+等频道 M3U 转换问题（#301）
- 优化频道匹配问题
- 优化地区选择空格情况

- Added FOFA cache to address access restrictions
- Fixed M3U conversion issues for channels like CCTV-5+ (#301)
- Optimized channel matching issues
- Improved handling of spaces in region selection

## v1.4.0

### 2024/9/5

- 注意：本次更新涉及配置变更，请以最新 config/config.ini 为准，工作流使用 user_config.ini 或 docker 挂载的用户请及时更新配置文件
- 新增组播源运行模式：FOFA、Tonkiang
- 新增支持组播源自定义维护频道 IP，目录位于 config/rtp，文件按“地区\_运营商”命名
- 优化测速方法，大幅提升组播源、酒店源的测速速度
- 优化频道名称匹配方法，支持模糊匹配，提高命中率
- 优化地区输入选择框
- 修复 driver 模式请求问题
- 修复组播地区选择全部时无法运行问题
- 修复工作流使用 user_config 时无法生成 m3u 结果问题

- Warning: This update involves configuration changes. Please refer to the latest config/config.ini. Users using user_config.ini or Docker-mounted configurations should update their configuration files promptly.
- Added multicast source operation modes: FOFA, Tonkiang.
- Added support for custom-maintained multicast source channel IPs, located in config/rtp, with files named by "region_operator".
- Optimized speed test method, significantly improving the speed test of multicast sources and hotel sources.
- Optimized channel name matching method to support fuzzy matching, increasing hit rate.
- Optimized region input selection box.
- Fixed an issue with driver mode requests.
- Fixed an issue where multicast would not run when all regions were selected.
- Fixed an issue where workflows using user_config could not generate m3u results.

## v1.3.9

### 2024/8/30

- 酒店源新增 ZoomEye 数据源，开启 FOFA 配置即可使用（Added ZoomEye data source to hotel sources, can be used by enabling FOFA configuration）
- 酒店源、组播源地区选项增加“全部”选项（Added "all" option to the region selection for hotel sources and multicast sources）
- 调整默认运行配置：关闭订阅源更新、Tonkiang 酒店源更新（Adjusted default runtime configuration: disabled subscription source updates and Tonkiang hotel source updates）

## v1.3.8

### 2024/8/29

- 更新组播地区 IP 缓存数据（Update multicast area IP cache data）
- 移除 source_channels 配置项（Remove source_channels configuration item）
- 优化模板频道名称匹配（Optimize template channel name matching）
- 优化进度条，显示接口处理进度（Optimize the progress bar to display the interface processing progress）
- UI 软件增加部分图标（Add some icons to the UI software）

## v1.3.7

### 2024/8/27

- 新增支持 M3U 结果格式转换，支持显示频道图标(open_m3u_result)（Added support for M3U result format conversion, including channel icon display (open_m3u_result)）
- 新增对于无结果的频道进行额外补充查询（Added additional queries for channels with no results）
- 增加控制使用 FFmpeg 开关(open_ffmpeg)（Added a switch to control the use of FFmpeg (open_ffmpeg)）
- 调整默认配置以酒店源模式运行（Adjusted default configuration to run in hotel source mode）
- 优化测速方法（Optimize Speed Test Method）
- 修复酒店源 CCTV 类等频道结果匹配异常（Fixed abnormal matching of results for hotel source CCTV channels）
- 修复组播源、酒店源 driver 运行问题（Fixed issues with multicast source and hotel source driver operation）
- 修复订阅源更新异常（Fixed subscription source update anomalies）

## v1.3.6

### 2024/8/22

- 新增酒店源更新，支持 Tonkiang、FOFA 两种工作模式（Added hotel source updates, supporting Tonkiang and FOFA working modes）
- 重构 UI 界面软件，新增帮助-关于、获取频道名称编辑、酒店源相关配置、软件图标（Refactored UI interface software, added Help-About, channel name editing, hotel source related configuration, and software icon）
- 新增测速日志页面服务，结果链接后添加/log 即可查看（Added a new speed test log page service. To view the results, simply add /log to the link）
- 移除关注频道相关配置（Removed configuration related to followed channels）
- 修复 Docker 定时任务未执行问题（Fixed issue with Docker scheduled tasks not executing）
- 修复使用历史结果时频道数据异常问题（Fixed issue with channel data anomalies when using historical results）
- 优化 UI 界面软件运行生成配置目录，方便查看与修改（Optimized UI interface software to generate configuration directory for easier viewing and modification）

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
