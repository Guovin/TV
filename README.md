# TVBox 电视直播源接口自动更新

根据基础模板直播源接口文件自动获取并更新最新直播源接口链接

## 特点

- 接口效验，过滤无效接口，排序规则：日期、速度、分辨率
- 定时执行，每隔 12 小时执行更新一次
- 可设置重点关注频道，单独配置获取分页的数量
- 分页结果获取（可配置页数、总接口数量）

## 使用方法

1. Fork 此项目，开启 Action 工作流可读写权限
2. 修改 demo.txt 模板文件，后续更新根据此文件内容进行更新
3. 修改 main.py(可选)：

- source_file：模板文件，默认值：demo.txt
- final_file：生成文件，默认值：result.txt
- important_list：关注频道名称列表
- important_page_num：关注频道获取分页数量，默认值：5
- default_page_num：常规频道获取分页数量，默认值：3
- urls_limit：接口数量，默认值：15
- filter_invalid_url：是否过滤无效接口，默认开启

4. result.txt 为更新后的直播源接口文件，source.json 为数据源文件

## License

[MIT](./LICENSE) License &copy; 2024-PRESENT [Govin](https://github.com/guovin)
