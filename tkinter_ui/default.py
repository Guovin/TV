import tkinter as tk
from utils.config import config
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
import os


class DefaultUI:

    def init_ui(self, root):
        """
        Init default UI
        """
        frame_default_open_update = tk.Frame(root)
        frame_default_open_update.pack(fill=tk.X)
        frame_default_open_update_column1 = tk.Frame(frame_default_open_update)
        frame_default_open_update_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_open_update_column2 = tk.Frame(frame_default_open_update)
        frame_default_open_update_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_update_label = tk.Label(
            frame_default_open_update_column1, text="开启更新:", width=8
        )
        self.open_update_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_update_var = tk.BooleanVar(value=config.open_update)
        self.open_update_checkbutton = ttk.Checkbutton(
            frame_default_open_update_column1,
            variable=self.open_update_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_update,
            text="(关闭则只运行结果页面服务)",
        )
        self.open_update_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_use_old_result_label = tk.Label(
            frame_default_open_update_column2, text="使用历史结果:", width=12
        )
        self.open_use_old_result_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_use_old_result_var = tk.BooleanVar(value=config.open_use_old_result)
        self.open_use_old_result_checkbutton = ttk.Checkbutton(
            frame_default_open_update_column2,
            variable=self.open_use_old_result_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_use_old_result,
            text="(保留上次更新可用结果)",
        )
        self.open_use_old_result_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_source_file = tk.Frame(root)
        frame_default_source_file.pack(fill=tk.X)
        frame_default_source_file_column1 = tk.Frame(frame_default_source_file)
        frame_default_source_file_column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_default_source_file_column2 = tk.Frame(frame_default_source_file)
        frame_default_source_file_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.source_file_label = tk.Label(
            frame_default_source_file_column1, text="模板文件:", width=8
        )
        self.source_file_entry = tk.Entry(frame_default_source_file_column1)
        self.source_file_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.source_file_entry.pack(fill=tk.X, padx=4, expand=True)
        self.source_file_entry.insert(0, config.source_file)

        self.source_file_button = tk.ttk.Button(
            frame_default_source_file_column2,
            text="选择文件",
            command=self.select_source_file,
        )
        self.source_file_button.pack(side=tk.LEFT, padx=4, pady=0)

        frame_default_final_file = tk.Frame(root)
        frame_default_final_file.pack(fill=tk.X)
        frame_default_final_file_column1 = tk.Frame(frame_default_final_file)
        frame_default_final_file_column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_default_final_file_column2 = tk.Frame(frame_default_final_file)
        frame_default_final_file_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.final_file_label = tk.Label(
            frame_default_final_file_column1, text="结果文件:", width=8
        )
        self.final_file_entry = tk.Entry(frame_default_final_file_column1)
        self.final_file_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.final_file_entry.pack(fill=tk.X, padx=4, expand=True)
        self.final_file_entry.insert(0, config.final_file)

        self.final_file_button = tk.ttk.Button(
            frame_default_final_file_column2,
            text="选择文件",
            command=self.select_final_file,
        )
        self.final_file_button.pack(side=tk.LEFT, padx=4, pady=0)

        frame_default_mode = tk.Frame(root)
        frame_default_mode.pack(fill=tk.X)
        frame_default_mode_params_column1 = tk.Frame(frame_default_mode)
        frame_default_mode_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_mode_params_column2 = tk.Frame(frame_default_mode)
        frame_default_mode_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_driver_label = tk.Label(
            frame_default_mode_params_column1, text="浏览器模式:", width=12
        )
        self.open_driver_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_driver_var = tk.BooleanVar(value=config.open_driver)
        self.open_driver_checkbutton = ttk.Checkbutton(
            frame_default_mode_params_column1,
            variable=self.open_driver_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_driver,
            text="(若获取更新异常请开启)",
        )
        self.open_driver_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_proxy_label = tk.Label(
            frame_default_mode_params_column2, text="开启代理:", width=12
        )
        self.open_proxy_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_proxy_var = tk.BooleanVar(value=config.open_proxy)
        self.open_proxy_checkbutton = ttk.Checkbutton(
            frame_default_mode_params_column2,
            variable=self.open_proxy_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_proxy,
            text="(通过代理进行更新)",
        )
        self.open_proxy_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_channel = tk.Frame(root)
        frame_default_channel.pack(fill=tk.X)
        frame_default_channel_column1 = tk.Frame(frame_default_channel)
        frame_default_channel_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_channel_column2 = tk.Frame(frame_default_channel)
        frame_default_channel_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.urls_limit_label = tk.Label(
            frame_default_channel_column1, text="频道接口数量:", width=12
        )
        self.urls_limit_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.urls_limit_entry = tk.Entry(frame_default_channel_column1, width=8)
        self.urls_limit_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.urls_limit_entry.insert(0, config.urls_limit)
        self.urls_limit_entry.bind("<KeyRelease>", self.update_urls_limit)

        self.ipv_type_label = tk.Label(
            frame_default_channel_column2, text="接口协议类型:", width=12
        )
        self.ipv_type_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.ipv_type_combo = ttk.Combobox(frame_default_channel_column2, width=5)
        self.ipv_type_combo.pack(side=tk.LEFT, padx=4, pady=8)
        self.ipv_type_combo["values"] = ("IPv4", "IPv6", "全部")
        if config.ipv_type == "ipv4":
            self.ipv_type_combo.current(0)
        elif config.ipv_type == "ipv6":
            self.ipv_type_combo.current(1)
        else:
            self.ipv_type_combo.current(2)
        self.ipv_type_combo.bind("<<ComboboxSelected>>", self.update_ipv_type)

        frame_default_open_keep_all = tk.Frame(root)
        frame_default_open_keep_all.pack(fill=tk.X)

        self.open_keep_all_label = tk.Label(
            frame_default_open_keep_all, text="保留模式:", width=12
        )
        self.open_keep_all_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_keep_all_var = tk.BooleanVar(value=config.open_keep_all)
        self.open_keep_all_checkbutton = ttk.Checkbutton(
            frame_default_open_keep_all,
            variable=self.open_keep_all_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_keep_all,
            text="(保留所有查询记录)",
        )
        self.open_keep_all_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_sort = tk.Frame(root)
        frame_default_sort.pack(fill=tk.X)
        frame_default_sort_column1 = tk.Frame(frame_default_sort)
        frame_default_sort_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_sort_column2 = tk.Frame(frame_default_sort)
        frame_default_sort_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_sort_label = tk.Label(
            frame_default_sort_column1, text="测速排序:", width=12
        )
        self.open_sort_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_sort_var = tk.BooleanVar(value=config.open_sort)
        self.open_sort_checkbutton = ttk.Checkbutton(
            frame_default_sort_column1,
            variable=self.open_sort_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_sort,
        )
        self.open_sort_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.sort_timeout_label = tk.Label(
            frame_default_sort_column2, text="测速超时:", width=12
        )
        self.sort_timeout_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.sort_timeout_entry = tk.Entry(frame_default_sort_column2, width=8)
        self.sort_timeout_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.sort_timeout_entry.insert(0, config.sort_timeout)
        self.sort_timeout_entry.bind("<KeyRelease>", self.update_sort_timeout)

        frame_default_sort_mode = tk.Frame(root)
        frame_default_sort_mode.pack(fill=tk.X)
        frame_default_sort_mode_column1 = tk.Frame(frame_default_sort_mode)
        frame_default_sort_mode_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_sort_mode_column2 = tk.Frame(frame_default_sort_mode)
        frame_default_sort_mode_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_ffmpeg_label = tk.Label(
            frame_default_sort_mode_column1, text="FFmpeg测速:", width=12
        )
        self.open_ffmpeg_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_ffmpeg_var = tk.BooleanVar(value=config.open_ffmpeg)
        self.open_ffmpeg_checkbutton = ttk.Checkbutton(
            frame_default_sort_mode_column1,
            variable=self.open_ffmpeg_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_ffmpeg,
            text="(需要手动安装)",
        )
        self.open_ffmpeg_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_m3u_result_label = tk.Label(
            frame_default_sort_mode_column2, text="M3U转换:", width=12
        )
        self.open_m3u_result_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_m3u_result_var = tk.BooleanVar(value=config.open_m3u_result)
        self.open_m3u_result_checkbutton = ttk.Checkbutton(
            frame_default_sort_mode_column2,
            variable=self.open_m3u_result_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_m3u_result,
            text="(开启频道图标)",
        )
        self.open_m3u_result_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_resolution_params = tk.Frame(root)
        frame_default_resolution_params.pack(fill=tk.X)
        frame_default_resolution_params_column1 = tk.Frame(
            frame_default_resolution_params
        )
        frame_default_resolution_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_resolution_params_column2 = tk.Frame(
            frame_default_resolution_params
        )
        frame_default_resolution_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_filter_resolution_label = tk.Label(
            frame_default_resolution_params_column1, text="分辨率过滤:", width=12
        )
        self.open_filter_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_filter_resolution_var = tk.BooleanVar(
            value=config.open_filter_resolution
        )
        self.open_filter_resolution_checkbutton = ttk.Checkbutton(
            frame_default_resolution_params_column1,
            variable=self.open_filter_resolution_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_filter_resolution,
            text="(低于最小分辨率将被过滤)",
        )
        self.open_filter_resolution_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.min_resolution_label = tk.Label(
            frame_default_resolution_params_column2, text="最小分辨率:", width=12
        )
        self.min_resolution_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_resolution_entry = tk.Entry(
            frame_default_resolution_params_column2, width=10
        )
        self.min_resolution_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.min_resolution_entry.insert(0, config.min_resolution)
        self.min_resolution_entry.bind("<KeyRelease>", self.update_min_resolution)

        frame_default_sort_params = tk.Frame(root)
        frame_default_sort_params.pack(fill=tk.X)
        frame_default_sort_params_column1 = tk.Frame(frame_default_sort_params)
        frame_default_sort_params_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_sort_params_column2 = tk.Frame(frame_default_sort_params)
        frame_default_sort_params_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.response_time_weight_label = tk.Label(
            frame_default_sort_params_column1, text="响应时间权重:", width=12
        )
        self.response_time_weight_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.response_time_weight_scale = tk.Scale(
            frame_default_sort_params_column1,
            from_=0,
            to=1,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            command=self.update_response_time_weight,
        )
        self.response_time_weight_scale.pack(side=tk.LEFT, padx=4, pady=8)
        self.response_time_weight_scale.set(config.response_time_weight)

        self.resolution_weight_label = tk.Label(
            frame_default_sort_params_column2, text="分辨率权重:", width=12
        )
        self.resolution_weight_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.resolution_weight_scale = tk.Scale(
            frame_default_sort_params_column2,
            from_=0,
            to=1,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            command=self.update_resolution_weight,
        )
        self.resolution_weight_scale.pack(side=tk.LEFT, padx=4, pady=8)
        self.resolution_weight_scale.set(config.resolution_weight)

        frame_default_open_update_info = tk.Frame(root)
        frame_default_open_update_info.pack(fill=tk.X)
        frame_default_open_update_info_column1 = tk.Frame(
            frame_default_open_update_info
        )
        frame_default_open_update_info_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_default_open_update_info_column2 = tk.Frame(
            frame_default_open_update_info
        )
        frame_default_open_update_info_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_update_time_label = tk.Label(
            frame_default_open_update_info_column1, text="显示更新时间:", width=12
        )
        self.open_update_time_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_update_time_var = tk.BooleanVar(value=config.open_update_time)
        self.open_update_time_checkbutton = ttk.Checkbutton(
            frame_default_open_update_info_column1,
            variable=self.open_update_time_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_update_time,
        )
        self.open_update_time_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_url_info_label = tk.Label(
            frame_default_open_update_info_column2, text="显示接口信息:", width=12
        )
        self.open_url_info_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_url_info_var = tk.BooleanVar(value=config.open_url_info)
        self.open_url_info_checkbutton = ttk.Checkbutton(
            frame_default_open_update_info_column2,
            variable=self.open_url_info_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_url_info,
        )
        self.open_url_info_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_open_empty_category = tk.Frame(root)
        frame_default_open_empty_category.pack(fill=tk.X)

        self.open_empty_category_label = tk.Label(
            frame_default_open_empty_category, text="显示无结果分类:", width=12
        )
        self.open_empty_category_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_empty_category_var = tk.BooleanVar(value=config.open_empty_category)
        self.open_empty_category_checkbutton = ttk.Checkbutton(
            frame_default_open_empty_category,
            variable=self.open_empty_category_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_empty_category,
        )
        self.open_empty_category_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_default_url_keywords_blacklist = tk.Frame(root)
        frame_default_url_keywords_blacklist.pack(fill=tk.X)

        self.url_keywords_blacklist_label = tk.Label(
            frame_default_url_keywords_blacklist, text="关键字黑名单:", width=12
        )
        self.url_keywords_blacklist_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.url_keywords_blacklist_text = scrolledtext.ScrolledText(
            frame_default_url_keywords_blacklist, height=5
        )
        self.url_keywords_blacklist_text.pack(
            side=tk.LEFT, padx=4, pady=8, expand=True, fill=tk.BOTH
        )
        self.url_keywords_blacklist_text.insert(
            tk.END, ",".join(config.url_keywords_blacklist)
        )
        self.url_keywords_blacklist_text.bind(
            "<KeyRelease>", self.update_url_keywords_blacklist
        )

    def update_open_update(self):
        config.set("Settings", "open_update", str(self.open_update_var.get()))

    def update_open_use_old_result(self):
        config.set(
            "Settings", "open_use_old_result", str(self.open_use_old_result_var.get())
        )

    def select_source_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择模板文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.source_file_entry.delete(0, tk.END)
            self.source_file_entry.insert(0, filepath)
            config.set("Settings", "source_file", filepath)

    def select_final_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择结果文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.final_file_entry.delete(0, tk.END)
            self.final_file_entry.insert(0, filepath)
            config.set("Settings", "final_file", filepath)

    def update_open_driver(self):
        config.set("Settings", "open_driver", str(self.open_driver_var.get()))

    def update_open_proxy(self):
        config.set("Settings", "open_proxy", str(self.open_proxy_var.get()))

    def update_open_keep_all(self):
        config.set("Settings", "open_keep_all", str(self.open_keep_all_var.get()))

    def update_open_sort(self):
        config.set("Settings", "open_sort", str(self.open_sort_var.get()))

    def update_sort_timeout(self):
        config.set("Settings", "sort_timeout", self.sort_timeout_entry.get())

    def update_open_ffmpeg(self):
        config.set("Settings", "open_ffmpeg", str(self.open_ffmpeg_var.get()))

    def update_open_m3u_result(self):
        config.set("Settings", "open_m3u_result", str(self.open_m3u_result_var.get()))

    def update_open_filter_resolution(self):
        config.set(
            "Settings",
            "open_filter_resolution",
            str(self.open_filter_resolution_var.get()),
        )

    def update_min_resolution(self, event):
        config.set("Settings", "min_resolution", self.min_resolution_entry.get())

    def update_urls_limit(self, event):
        config.set("Settings", "urls_limit", self.urls_limit_entry.get())

    def update_response_time_weight(self, event):
        weight1 = self.response_time_weight_scale.get()
        weight2 = 1 - weight1
        self.resolution_weight_scale.set(weight2)
        config.set("Settings", "response_time_weight", str(weight1))
        config.set("Settings", "resolution_weight", str(weight2))

    def update_resolution_weight(self, event):
        weight1 = self.resolution_weight_scale.get()
        weight2 = 1 - weight1
        self.response_time_weight_scale.set(weight2)
        config.set("Settings", "resolution_weight", str(weight1))
        config.set("Settings", "response_time_weight", str(weight2))

    def update_open_update_time(self):
        config.set("Settings", "open_update_time", str(self.open_update_time_var.get()))

    def update_open_url_info(self):
        config.set("Settings", "open_url_info", str(self.open_url_info_var.get()))

    def update_open_empty_category(self):
        config.set(
            "Settings", "open_empty_category", str(self.open_empty_category_var.get())
        )

    def update_ipv_type(self, event):
        config.set("Settings", "ipv_type", self.ipv_type_combo.get())

    def update_url_keywords_blacklist(self, event):
        config.set(
            "Settings",
            "url_keywords_blacklist",
            self.url_keywords_blacklist_text.get(1.0, tk.END),
        )

    def update_url_keywords_blacklist(self, event):
        config.set(
            "Settings",
            "url_keywords_blacklist",
            self.url_keywords_blacklist_text.get(1.0, tk.END),
        )

    def change_entry_state(self, state):
        for entry in [
            "open_update_checkbutton",
            "open_use_old_result_checkbutton",
            "open_driver_checkbutton",
            "open_proxy_checkbutton",
            "source_file_entry",
            "source_file_button",
            "final_file_entry",
            "final_file_button",
            "open_keep_all_checkbutton",
            "open_sort_checkbutton",
            "sort_timeout_entry",
            "open_ffmpeg_checkbutton",
            "open_m3u_result_checkbutton",
            "open_filter_resolution_checkbutton",
            "min_resolution_entry",
            "urls_limit_entry",
            "response_time_weight_scale",
            "resolution_weight_scale",
            "open_update_time_checkbutton",
            "open_url_info_checkbutton",
            "open_empty_category_checkbutton",
            "ipv_type_combo",
            "url_keywords_blacklist_text",
        ]:
            getattr(self, entry).config(state=state)
