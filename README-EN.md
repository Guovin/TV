# TVBox Custom Channel Menu and Live Source Interface Auto-update

Customize channel menus, automatically fetch and update the latest live source interfaces based on the template file, and generate usable channel interface files.

[中文](./README.md) | English

## Features

- Customize templates to generate the channel categories and order you want
- Interface validation to filter out invalid interfaces
- Comprehensive sorting based on response time and resolution
  <s>
- Scheduled execution, updates every day at 8:00 am Beijing time
- The maximum number of update channels is 200
  </s>
- Set up key focus channels and configure the number of pages fetched separately
- Pagination results retrieval (configurable number of pages and interfaces)
- Ensure update timeliness, configure to retrieve interfaces updated within a recent time range
- Can filter ipv4, ipv6 interfaces
- Blacklist feature: Interface domain and keywords

## Config

| Configuration Item     | Default Value      | Description                                                                                                        |
| ---------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------ |
| source_file            | "demo.txt"         | Template file name                                                                                                 |
| final_file             | "result.txt"       | Generated file name                                                                                                |
| favorite_list          | ["CCTV1","CCTV13"] | List of favorite channel names (used only to distinguish from regular channels, custom page retrieval quantity)    |
| favorite_page_num      | 6                  | Page retrieval quantity for favorite channels                                                                      |
| default_page_num       | 4                  | Page retrieval quantity for regular channels                                                                       |
| urls_limit             | 15                 | Number of interfaces per channel                                                                                   |
| response_time_weight   | 0.5                | Response time weight value (the sum of all weight values should be 1)                                              |
| resolution_weight      | 0.5                | Resolution weight value (the sum of all weight values should be 1)                                                 |
| recent_days            | 30                 | Retrieve interfaces updated within a recent time range (in days), reducing appropriately can avoid matching issues |
| ipv_type               | "ipv4"             | The type of interface in the generated result, optional values: "ipv4", "ipv6", "all"                              |
| domain_blacklist       | ["epg.pw"]         | Interface domain blacklist, used to filter out interfaces with low-quality, ad-inclusive domains                   |
| url_keywords_blacklist | []                 | Interface keyword blacklist, used to filter out interfaces containing specific characters                          |

## Quick Start

For detailed tutorial, please see [Quick Start](./docs/tutorial-EN.md)

## Changelog

[Changelog](./CHANGELOG.md)

## Disclaimer

This project is provided for programming learning and research resources. The data collected in the project comes from the network, and the developer does not make any guarantees about the accuracy, completeness, or reliability of the data.

The developer is not responsible for any direct or indirect losses that may be caused by the use of these codes or data. Users should judge the legality and risk of their use by themselves.

The code and data of this project are only for learning and research use, and must not be used for any commercial purposes. Anyone or organization should abide by relevant laws and regulations when using it, respect and protect the rights and interests of developers.

If you use the code or data of this project, it means that you have understood and agreed to this disclaimer. If you do not agree with this disclaimer, you should stop using the code and data of this project immediately.

In addition, the code and data of this project may be updated irregularly, but there is no guarantee of the timeliness and accuracy of the update, nor the stability and functionality of the code.

In any case, the developer and any contributor do not assume any responsibility for any damage or other liability caused by the use or inability to use the code or data of this project.

Using the code or data of this project means that you have understood and accepted these terms.

## GitHub Terms of Service

When forking or using this project, you must comply with the [GitHub Terms of Service](https://docs.github.com/en/github/site-policy/github-terms-of-service). This includes, but is not limited to, the prohibition of uploading content that infringes copyright, is illegal, malicious, or violates our terms. Any violation of these provisions may result in the termination of your account. When using this project, please ensure that your behavior complies with these provisions.

If you do not agree to comply with these terms, you should stop using the code and data of this project immediately.

The use of the code or data of this project means that you have understood and accepted these terms.

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
