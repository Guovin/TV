# 更新日志（Changelog）

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
