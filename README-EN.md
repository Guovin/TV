Automatically obtain and update the latest live broadcast interface link according to the basic template live broadcast source interface file

[中文](./README.md) | English

## Features

- Interface verification, filter invalid interfaces, sorting rules: date, speed, resolution
- Scheduled execution, updated every 12 hours
- You can set key focus channels and configure the number of pages to get separately
- Pagination results acquisition (configurable number of pages, total number of interfaces)

## How to Use

1. Fork this project, turn on Action workflow read and write permissions, Settings → Actions → General → Workflow permissions → Read and write permissions → Save
2. Modify the demo.txt template file, subsequent updates will be based on the content of this file
3. Modify config.py (optional):

- source_file: Template file, default value: demo.txt
- final_file: Generated file, default value: result.txt
- favorite_list: List of focus channel names
- favorite_page_num: Number of pages to get for focus channels, default value: 5
- default_page_num: Number of pages to get for regular channels, default value: 3
- urls_limit: Number of interfaces, default value: 15
- filter_invalid_url: Whether to filter invalid interfaces, default: True

4. result.txt is the updated live broadcast interface file, source.json is the data source file

## Disclaimer

This project is for providing resources for programming learning and research. The data collected in the project comes from the Internet, and the developer does not guarantee the accuracy, completeness, or reliability of the data.

The developer is not responsible for any direct or indirect losses that may be caused by the use of these codes or data. Users should judge the legality and risk of their use on their own.

The code and data of this project are for learning and research purposes only and must not be used for any commercial purposes. Anyone or organization using it should comply with relevant laws and regulations, respect and protect the rights and interests of developers.

If you use the code or data of this project, it means that you have understood and agreed to this disclaimer. If you do not agree with this disclaimer, you should stop using the code and data of this project immediately.

In addition, the code and data of this project may be updated from time to time, but there is no guarantee of the timeliness and accuracy of the updates, nor the stability and functionality of the code.

In any case, the developer and any contributor do not assume any responsibility for any damage or other liability caused by the use or inability to use the code or data of this project.

Using the code or data of this project means that you have understood and accepted these terms.

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
