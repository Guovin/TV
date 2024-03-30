# Changelog

## v1.0.0

### 2024/3/30

- 修复工作流读取配置与更新文件对比问题

---

- Fix the issue of workflow reading configuration and comparing updated files

### 2024/3/29

- 修复用户专属配置更新结果失败

---

- Fix user specific configuration update failure

### 2024/3/26

- 新增快速上手-详细教程
- 新增以 releases 发布版本更新信息

---

- Add a Quick Start - detailed tutorial
- Add release notes for version updates using releases

### 2024/3/25

- 增加代码防覆盖，用户可使用 user\_作为文件前缀以区分独有配置，可避免在合并更新时本地代码被上游仓库代码覆盖，如 user_config.py、user_demo.txt、user_result.txt

---

- Add code anti-overwriting. Users can use user\_ as the file prefix to distinguish unique configurations. This prevents local codes from being overwritten by upstream repository codes, such as user_config.py, user_demo.txt, and user_result.txt, when merging updates

### 2024/3/21

- 修复潜在的更新文件追踪失效，导致更新失败
- 调整最近更新获取时间默认为 30 天
- 优化最近更新接口筛选，当筛选后不足指定接口个数时，将使用其它时间范围的可用接口补充
- 优化珠江、CCTV 频道匹配问题
- 移除推送实时触发更新

---

- Fixed potential tracking failure of updated files, leading to update failure
- Adjusted the default recent update retrieval time to 30 days
- Optimized the recent update interface filter, when the number of interfaces is insufficient after filtering, other time range available interfaces will be used for supplementation
- Optimized the matching problem of Zhujiang and CCTV channels
- Removed push real-time trigger update

### 2024/3/18

- 新增配置项：ipv_type，用于过滤 ipv4、ipv6 接口类型
- 优化文件更新逻辑，避免更新失效引起文件丢失
- 调整分页获取默认值：关注频道获取 6 页，常规频道获取 4 页，以提升更新速度
- 增加接口日志文件 result.log 输出
- 修复权重排序异常

---

- Added configuration item: ipv_type, used to filter ipv4, ipv6 interface types
- Optimized file update logic to prevent file loss caused by update failure
- Adjusted the default value for pagination: fetch 6 pages for followed channels, 4 pages for regular channels, to improve update speed
- Added output of interface log file result.log
- Fixed weight sorting anomaly

### 2024/3/15

- 优化代码结构
- 新增接口日志，记录详细质量指标
- 新增可手动运行工作流触发更新

---

- Optimize code structure
- Added interface logs to record detailed quality indicators
- Added manual workflows to trigger updates

### 2024/3/13

- 增加配置项：recent_days，筛选获取最近时间范围内更新的接口，默认最近 60 天
- 调整默认值：关注频道获取 8 页，常规频道获取 5 页

---

- Added configuration item: recent_days, a filter to get the most recently updated interfaces, default to the last 60 days
- Adjusted default values: fetch 8 pages for followed channels, 5 pages for regular channels

### 2024/3/6

- 更新文件代理说明

---

- Update file proxy description

### 2024/3/4

- 增加配置项：响应时间与分辨率权重值
- 移除配置项：是否过滤无效接口，始终执行过滤
- 移除按日期排序，采用响应时间与分辨率作为排序规则
- 更新 README：增加修改更新频率、文件代理说明、更新日志

---

- Added configuration items: response time and resolution weight values
- Removed configuration items: whether to filter invalid interfaces, always perform filtering
- Removed sorting by date, using response time and resolution as sorting rules
- Updated README: added modification update frequency, file proxy description, update log
