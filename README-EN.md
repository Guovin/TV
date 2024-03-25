# TVBox Custom Channel Menu and Live Source Interface Auto-update

Customize channel menus, automatically fetch and update the latest live source interfaces based on the template file, and generate usable channel interface files.

[中文](./README.md) | English

## Features

- Customize templates to generate the channel categories and order you want
- Interface validation to filter out invalid interfaces
- Comprehensive sorting based on response time and resolution
- Scheduled execution, updates every 12 hours
- Set up key focus channels and configure the number of pages fetched separately
- Pagination results retrieval (configurable number of pages and interfaces)
- Ensure update timeliness, configure to retrieve interfaces updated within a recent time range
- Can filter ipv4, ipv6 interfaces

## How to Use

1. Fork this project and enable read and write permissions for the Action workflow:

   - Settings → Actions → General → Workflow permissions → Read and write permissions → Save

2. Modify the demo.txt template file to the channel categories and order you want. Subsequent updates will be based on the content of this file.
3. Modify the configuration (optional):

   #### config.py:

   | Configuration Item   | Default Value      | Description                                                                                                        |
   | -------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------ |
   | source_file          | "demo.txt"         | Template file name                                                                                                 |
   | final_file           | "result.txt"       | Generated file name                                                                                                |
   | favorite_list        | ["CCTV1","CCTV13"] | List of favorite channel names (used only to distinguish from regular channels, custom page retrieval quantity)    |
   | favorite_page_num    | 6                  | Page retrieval quantity for favorite channels                                                                      |
   | default_page_num     | 4                  | Page retrieval quantity for regular channels                                                                       |
   | urls_limit           | 15                 | Number of interfaces per channel                                                                                   |
   | response_time_weight | 0.5                | Response time weight value (the sum of all weight values should be 1)                                              |
   | resolution_weight    | 0.5                | Resolution weight value (the sum of all weight values should be 1)                                                 |
   | recent_days          | 30                 | Retrieve interfaces updated within a recent time range (in days), reducing appropriately can avoid matching issues |
   | ipv_type             | "ipv4"             | The type of interface in the generated result, optional values: "ipv4", "ipv6", "all"                              |

   #### .github/workflows/main.yml:

   - If you want to modify the update frequency (default is 12 hours), you can modify the on:schedule:- cron field

4. result.txt is the updated live source interface file, source.json is the data source file (currently only for sharing)
5. It is recommended to access the live source and data source files via proxy:
   - https://mirror.ghproxy.com/raw.githubusercontent.com/username/repository-name/master/result.txt
   - https://mirror.ghproxy.com/raw.githubusercontent.com/username/repository-name/master/source.json

## Update Log

### 2024/3/25

- Add code anti-overwriting. Users can use user\_ as the file prefix to distinguish unique configurations. This prevents local codes from being overwritten by upstream repository codes, such as user_config.py, user_demo.txt, and user_result.txt, when merging updates

### 2024/3/21

- Fixed potential tracking failure of updated files, leading to update failure
- Adjusted the default recent update retrieval time to 30 days
- Optimized the recent update interface filter, when the number of interfaces is insufficient after filtering, other time range available interfaces will be used for supplementation
- Optimized the matching problem of Zhujiang and CCTV channels
- Removed push real-time trigger update

### 2024/3/18

- Added configuration item: ipv_type, used to filter ipv4, ipv6 interface types
- Optimized file update logic to prevent file loss caused by update failure
- Adjusted the default value for pagination: fetch 6 pages for followed channels, 4 pages for regular channels, to improve update speed
- Added output of interface log file result.log
- Fixed weight sorting anomaly

### 2024/3/15

- Optimize code structure
- Added interface logs to record detailed quality indicators
- Added manual workflows to trigger updates

### 2024/3/13

- Added configuration item: recent_days, a filter to get the most recently updated interfaces, default to the last 60 days
- Adjusted default values: fetch 8 pages for followed channels, 5 pages for regular channels

### 2024/3/6

- Update file proxy description

### 2024/3/4

- Added configuration items: response time and resolution weight values
- Removed configuration items: whether to filter invalid interfaces, always perform filtering
- Removed sorting by date, using response time and resolution as sorting rules
- Updated README: added modification update frequency, file proxy description, update log

## Disclaimer

This project is provided for programming learning and research resources. The data collected in the project comes from the network, and the developer does not make any guarantees about the accuracy, completeness, or reliability of the data.

The developer is not responsible for any direct or indirect losses that may be caused by the use of these codes or data. Users should judge the legality and risk of their use by themselves.

The code and data of this project are only for learning and research use, and must not be used for any commercial purposes. Anyone or organization should abide by relevant laws and regulations when using it, respect and protect the rights and interests of developers.

If you use the code or data of this project, it means that you have understood and agreed to this disclaimer. If you do not agree with this disclaimer, you should stop using the code and data of this project immediately.

In addition, the code and data of this project may be updated irregularly, but there is no guarantee of the timeliness and accuracy of the update, nor the stability and functionality of the code.

In any case, the developer and any contributor do not assume any responsibility for any damage or other liability caused by the use or inability to use the code or data of this project.

Using the code or data of this project means that you have understood and accepted these terms.

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
