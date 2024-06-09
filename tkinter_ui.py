import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import filedialog
from utils import resource_path, load_external_config
from main import UpdateSource
import os

config_path = resource_path("user_config.py")
default_config_path = resource_path("config.py")
config = (
    load_external_config("user_config.py")
    if os.path.exists(config_path)
    else load_external_config("config.py")
)


class TkinterUI:

    def __init__(self, root):
        self.root = root
        self.root.title("直播源接口更新工具")
        self.version = "v1.0.0"
        self.update_source = UpdateSource()
        self.update_running = False
        self.config_entrys = [
            "source_file_entry",
            "source_file_button",
            "final_file_entry",
            "final_file_button",
            "open_subscribe_checkbutton",
            "open_multicast_checkbutton",
            "open_online_search_checkbutton",
            "open_sort_checkbutton",
            "favorite_list_text",
            "favorite_page_num_entry",
            "default_page_num_entry",
            "urls_limit_entry",
            "response_time_weight_entry",
            "resolution_weight_entry",
            "ipv_type_combo",
            "recent_days_entry",
            "domain_blacklist_text",
            "url_keywords_blacklist_text",
            "subscribe_urls_text",
            "region_list_text",
        ]

    def format_list(self, text):
        return [f"{item.strip()}" for item in text.split(",") if item.strip()]

    def select_source_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择模板文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.source_file_entry.delete(0, tk.END)
            self.source_file_entry.insert(0, filepath)
            config.source_file = f'"{filepath}"'

    def select_final_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(), title="选择结果文件", filetypes=[("txt", "*.txt")]
        )
        if filepath:
            self.final_file_entry.delete(0, tk.END)
            self.final_file_entry.insert(0, filepath)
            config.final_file = f'"{filepath}"'

    def update_open_subscribe(self):
        config.open_subscribe = self.open_subscribe_var.get()

    def update_open_multicast(self):
        config.open_multicast = self.open_multicast_var.get()

    def update_open_online_search(self):
        config.open_online_search = self.open_online_search_var.get()

    def update_open_sort(self):
        config.open_sort = self.open_sort_var.get()

    def update_favorite_list(self, event):
        config.favorite_list = self.format_list(
            self.favorite_list_text.get(1.0, tk.END)
        )

    def update_favorite_page_num(self, event):
        config.favorite_page_num = self.favorite_page_num_entry.get()

    def update_default_page_num(self, event):
        config.default_page_num = self.default_page_num_entry.get()

    def update_urls_limit(self, event):
        config.urls_limit = self.urls_limit_entry.get()

    def update_response_time_weight(self, event):
        config.response_time_weight = self.response_time_weight_entry.get()

    def update_resolution_weight(self, event):
        config.resolution_weight = self.resolution_weight_entry.get()

    def update_ipv_type(self, event):
        config.ipv_type = f'"{self.ipv_type_combo.get()}"'

    def update_recent_days(self, event):
        config.recent_days = self.recent_days_entry.get()

    def update_url_keywords_blacklist(self, event):
        config.url_keywords_blacklist = self.format_list(
            self.url_keywords_blacklist_text.get(1.0, tk.END)
        )

    def update_domain_blacklist(self, event):
        config.domain_blacklist = self.format_list(
            self.domain_blacklist_text.get(1.0, tk.END)
        )

    def update_url_keywords_blacklist(self, event):
        config.url_keywords_blacklist = self.format_list(
            self.url_keywords_blacklist_text.get(1.0, tk.END)
        )

    def update_subscribe_urls(self, event):
        config.subscribe_urls = self.format_list(
            self.subscribe_urls_text.get(1.0, tk.END)
        )

    def update_region_list(self, event):
        config.region_list = self.format_list(self.region_list_text.get(1.0, tk.END))

    def save_config(self):
        config_values = {
            "source_file": f'"{self.source_file_entry.get()}"',
            "final_file": f'"{self.final_file_entry.get()}"',
            "favorite_list": self.format_list(self.favorite_list_text.get(1.0, tk.END)),
            "open_online_search": self.open_online_search_var.get(),
            "favorite_page_num": self.favorite_page_num_entry.get(),
            "default_page_num": self.default_page_num_entry.get(),
            "urls_limit": self.urls_limit_entry.get(),
            "open_sort": self.open_sort_var.get(),
            "response_time_weight": self.response_time_weight_entry.get(),
            "resolution_weight": self.resolution_weight_entry.get(),
            "recent_days": self.recent_days_entry.get(),
            "ipv_type": f'"{self.ipv_type_combo.get()}"',
            "domain_blacklist": self.format_list(
                self.domain_blacklist_text.get(1.0, tk.END)
            ),
            "url_keywords_blacklist": self.format_list(
                self.url_keywords_blacklist_text.get(1.0, tk.END)
            ),
            "open_subscribe": self.open_subscribe_var.get(),
            "subscribe_urls": self.format_list(
                self.subscribe_urls_text.get(1.0, tk.END)
            ),
            "open_multicast": self.open_multicast_var.get(),
            "region_list": self.format_list(self.region_list_text.get(1.0, tk.END)),
        }

        for key, value in config_values.items():
            setattr(config, key, value)
        user_config_file = (
            "user_config.py" if os.path.exists("user_config.py") else "config.py"
        )
        with open(
            resource_path(user_config_file, persistent=True), "w", encoding="utf-8"
        ) as f:
            for key, value in config_values.items():
                f.write(f"{key} = {value}\n")
        messagebox.showinfo("提示", "保存成功")

    def run_update(self):
        self.update_running = not self.update_running
        if self.update_running:
            self.run_button.config(text="取消更新", state="normal")
            for entry in self.config_entrys:
                getattr(self, entry).config(state="disabled")
            self.progress_bar["value"] = 0
            self.progress_label.pack()
            self.progress_bar.pack()
            self.update_source.start(self.update_progress)
        else:
            self.update_source.stop()
            self.run_button.config(text="开始更新", state="normal")
            for entry in self.config_entrys:
                getattr(self, entry).config(state="normal")
            self.progress_bar.pack_forget()
            self.progress_label.pack_forget()

    def update_progress(self, title, progress, finished=False):
        self.progress_bar["value"] = progress
        self.progress_label["text"] = f"{title}, 进度: {progress}%"
        self.root.update()
        if finished:
            self.run_button.config(text="开始更新", state="normal")
            self.update_running = False
            for entry in self.config_entrys:
                getattr(self, entry).config(state="normal")

    def init_UI(self):

        row1 = tk.Frame(self.root)
        row1.pack(fill=tk.X)
        row1_column1 = tk.Frame(row1)
        row1_column1.pack(side=tk.LEFT, fill=tk.Y)
        row1_column2 = tk.Frame(row1)
        row1_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_subscribe_label = tk.Label(row1_column1, text="开启订阅源:", width=14)
        self.open_subscribe_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.open_subscribe_var = tk.BooleanVar(value=config.open_subscribe)
        self.open_subscribe_checkbutton = ttk.Checkbutton(
            row1_column1,
            width=12,
            variable=self.open_subscribe_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_subscribe,
        )
        self.open_subscribe_checkbutton.pack(side=tk.LEFT, padx=4, pady=4)

        self.open_multicast_label = tk.Label(row1_column2, text="开启组播源:", width=14)
        self.open_multicast_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.open_multicast_var = tk.BooleanVar(value=config.open_multicast)
        self.open_multicast_checkbutton = ttk.Checkbutton(
            row1_column2,
            width=12,
            variable=self.open_multicast_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_multicast,
        )
        self.open_multicast_checkbutton.pack(side=tk.LEFT, padx=4, pady=4)

        row2 = tk.Frame(self.root)
        row2.pack(fill=tk.X)
        row2_column1 = tk.Frame(row2)
        row2_column1.pack(side=tk.LEFT, fill=tk.Y)
        row2_column2 = tk.Frame(row2)
        row2_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_online_search_label = tk.Label(
            row2_column1, text="开启线上搜索:", width=14
        )
        self.open_online_search_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.open_online_search_var = tk.BooleanVar(value=config.open_online_search)
        self.open_online_search_checkbutton = ttk.Checkbutton(
            row2_column1,
            width=12,
            variable=self.open_online_search_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_online_search,
        )
        self.open_online_search_checkbutton.pack(side=tk.LEFT, padx=4, pady=4)

        self.open_sort_label = tk.Label(row2_column2, text="开启测速排序:", width=14)
        self.open_sort_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.open_sort_var = tk.BooleanVar(value=config.open_sort)
        self.open_sort_checkbutton = ttk.Checkbutton(
            row2_column2,
            width=12,
            variable=self.open_sort_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_sort,
        )
        self.open_sort_checkbutton.pack(side=tk.LEFT, padx=4, pady=4)

        row3 = tk.Frame(self.root)
        row3.pack(fill=tk.X)
        row3_column1 = tk.Frame(row3)
        row3_column1.pack(side=tk.LEFT, fill=tk.Y)
        row3_column2 = tk.Frame(row3)
        row3_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.source_file_label = tk.Label(row3_column1, text="模板文件:", width=14)
        self.source_file_entry = tk.Entry(row3_column1)
        self.source_file_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.source_file_entry.pack(fill=tk.X, padx=4, expand=True)
        self.source_file_entry.insert(0, config.source_file)

        self.source_file_button = tk.Button(
            row3_column1, text="选择文件", command=self.select_source_file
        )
        self.source_file_button.pack(side=tk.LEFT, padx=4, pady=4)

        self.final_file_label = tk.Label(row3_column2, text="结果文件:", width=14)
        self.final_file_entry = tk.Entry(row3_column2)
        self.final_file_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.final_file_entry.pack(fill=tk.X, padx=4, expand=True)
        self.final_file_entry.insert(0, config.final_file)

        self.final_file_button = tk.Button(
            row3_column2, text="选择文件", command=self.select_final_file
        )
        self.final_file_button.pack(side=tk.LEFT, padx=4, pady=4)

        row4 = tk.Frame(self.root)
        row4.pack(fill=tk.X)

        self.favorite_list_label = tk.Label(row4, text="关注频道:", width=14)
        self.favorite_list_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.favorite_list_text = scrolledtext.ScrolledText(row4, height=5)
        self.favorite_list_text.pack(
            side=tk.LEFT, padx=4, pady=4, expand=True, fill=tk.BOTH
        )
        self.favorite_list_text.insert(tk.END, ",".join(config.favorite_list))
        self.favorite_list_text.bind("<KeyRelease>", self.update_favorite_list)

        row5 = tk.Frame(self.root)
        row5.pack(fill=tk.X)
        row5_column1 = tk.Frame(row5)
        row5_column1.pack(side=tk.LEFT, fill=tk.Y)
        row5_column2 = tk.Frame(row5)
        row5_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.favorite_page_num_label = tk.Label(
            row5_column1, text="关注获取页数:", width=14
        )
        self.favorite_page_num_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.favorite_page_num_entry = tk.Entry(row5_column1)
        self.favorite_page_num_entry.pack(side=tk.LEFT, padx=4, pady=4)
        self.favorite_page_num_entry.insert(0, config.favorite_page_num)
        self.favorite_page_num_entry.bind("<KeyRelease>", self.update_favorite_page_num)

        self.default_page_num_label = tk.Label(
            row5_column2, text="默认获取页数:", width=14
        )
        self.default_page_num_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.default_page_num_entry = tk.Entry(row5_column2)
        self.default_page_num_entry.pack(side=tk.LEFT, padx=4, pady=4)
        self.default_page_num_entry.insert(0, config.default_page_num)
        self.default_page_num_entry.bind("<KeyRelease>", self.update_default_page_num)

        row6 = tk.Frame(self.root)
        row6.pack(fill=tk.X)
        row6_column1 = tk.Frame(row6)
        row6_column1.pack(side=tk.LEFT, fill=tk.Y)
        row6_column2 = tk.Frame(row6)
        row6_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.urls_limit_label = tk.Label(
            row6_column1, text="单个频道接口数量:", width=14
        )
        self.urls_limit_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.urls_limit_entry = tk.Entry(row6_column1)
        self.urls_limit_entry.pack(side=tk.LEFT, padx=4, pady=4)
        self.urls_limit_entry.insert(15, config.urls_limit)
        self.urls_limit_entry.bind("<KeyRelease>", self.update_urls_limit)

        self.ipv_type_label = tk.Label(row6_column2, text="接口协议类型:", width=14)
        self.ipv_type_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.ipv_type_combo = ttk.Combobox(row6_column2)
        self.ipv_type_combo.pack(side=tk.LEFT, padx=4, pady=4)
        self.ipv_type_combo["values"] = ("ipv4", "ipv6", "all")
        self.ipv_type_combo.current(0)
        self.ipv_type_combo.bind("<<ComboboxSelected>>", self.update_ipv_type)

        row7 = tk.Frame(self.root)
        row7.pack(fill=tk.X)
        row7_column1 = tk.Frame(row7)
        row7_column1.pack(side=tk.LEFT, fill=tk.Y)
        row7_column2 = tk.Frame(row7)
        row7_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.response_time_weight_label = tk.Label(
            row7_column1, text="响应时间权重:", width=14
        )
        self.response_time_weight_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.response_time_weight_entry = tk.Entry(row7_column1)
        self.response_time_weight_entry.pack(side=tk.LEFT, padx=4, pady=4)
        self.response_time_weight_entry.insert(0, config.response_time_weight)
        self.response_time_weight_entry.bind(
            "<KeyRelease>", self.update_response_time_weight
        )

        self.resolution_weight_label = tk.Label(
            row7_column2, text="分辨率权重:", width=14
        )
        self.resolution_weight_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.resolution_weight_entry = tk.Entry(row7_column2)
        self.resolution_weight_entry.pack(side=tk.LEFT, padx=4, pady=4)
        self.resolution_weight_entry.insert(0, config.resolution_weight)
        self.resolution_weight_entry.bind("<KeyRelease>", self.update_resolution_weight)

        row8 = tk.Frame(self.root)
        row8.pack(fill=tk.X)

        self.recent_days_label = tk.Label(row8, text="获取时间范围(天):", width=14)
        self.recent_days_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.recent_days_entry = tk.Entry(row8)
        self.recent_days_entry.pack(side=tk.LEFT, padx=4, pady=4)
        self.recent_days_entry.insert(30, config.recent_days)
        self.recent_days_entry.bind("<KeyRelease>", self.update_recent_days)

        row9 = tk.Frame(self.root)
        row9.pack(fill=tk.X)

        self.domain_blacklist_label = tk.Label(row9, text="域名黑名单:", width=14)
        self.domain_blacklist_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.domain_blacklist_text = scrolledtext.ScrolledText(row9, height=5)
        self.domain_blacklist_text.pack(
            side=tk.LEFT, padx=4, pady=4, expand=True, fill=tk.BOTH
        )
        self.domain_blacklist_text.insert(tk.END, ",".join(config.domain_blacklist))
        self.domain_blacklist_text.bind("<KeyRelease>", self.update_domain_blacklist)

        row10 = tk.Frame(self.root)
        row10.pack(fill=tk.X)

        self.url_keywords_blacklist_label = tk.Label(
            row10, text="关键字黑名单:", width=14
        )
        self.url_keywords_blacklist_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.url_keywords_blacklist_text = scrolledtext.ScrolledText(row10, height=5)
        self.url_keywords_blacklist_text.pack(
            side=tk.LEFT, padx=4, pady=4, expand=True, fill=tk.BOTH
        )
        self.url_keywords_blacklist_text.insert(
            tk.END, ",".join(config.url_keywords_blacklist)
        )
        self.url_keywords_blacklist_text.bind(
            "<KeyRelease>", self.update_url_keywords_blacklist
        )

        row11 = tk.Frame(self.root)
        row11.pack(fill=tk.X)

        self.subscribe_urls_label = tk.Label(row11, text="订阅源:", width=14)
        self.subscribe_urls_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.subscribe_urls_text = scrolledtext.ScrolledText(row11, height=5)
        self.subscribe_urls_text.pack(
            side=tk.LEFT, padx=4, pady=4, expand=True, fill=tk.BOTH
        )
        self.subscribe_urls_text.insert(tk.END, ",".join(config.subscribe_urls))
        self.subscribe_urls_text.bind("<KeyRelease>", self.update_subscribe_urls)

        row12 = tk.Frame(self.root)
        row12.pack(fill=tk.X)

        self.region_list_label = tk.Label(row12, text="组播地区:", width=14)
        self.region_list_label.pack(side=tk.LEFT, padx=4, pady=4)
        self.region_list_text = scrolledtext.ScrolledText(row12, height=5)
        self.region_list_text.pack(
            side=tk.LEFT, padx=4, pady=4, expand=True, fill=tk.BOTH
        )
        self.region_list_text.insert(tk.END, ",".join(config.region_list))
        self.region_list_text.bind("<KeyRelease>", self.update_region_list)

        row13 = tk.Frame(self.root)
        row13.pack(fill=tk.X, pady=10, padx=120)
        row13_column1 = tk.Frame(row13)
        row13_column1.pack(side=tk.LEFT, fill=tk.Y)
        row13_column2 = tk.Frame(row13)
        row13_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.save_button = tk.Button(
            row13_column1, text="保存设置", command=self.save_config
        )
        self.save_button.pack(side=tk.LEFT, padx=4, pady=4)

        self.run_button = tk.Button(
            row13_column2, text="开始更新", command=self.run_update
        )
        self.run_button.pack(side=tk.LEFT, padx=4, pady=4)

        version_frame = tk.Frame(self.root)
        version_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.version_label = tk.Label(
            version_frame, text=self.version, fg="gray", anchor="se"
        )
        self.version_label.pack(side=tk.RIGHT, padx=5, pady=5)

        row14 = tk.Frame(self.root)
        row14.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(row14, length=300, mode="determinate")
        self.progress_bar.pack_forget()
        self.progress_label = tk.Label(row14, text="进度: 0%")
        self.progress_label.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_ui = TkinterUI(root)
    tkinter_ui.init_UI()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = 500
    height = 780
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry("%dx%d+%d+%d" % (width, height, x, y))
    root.mainloop()
