import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk
import threading

try:
    import user_config as config
except ImportError:
    import config
from main import UpdateSource
import os


class TkinterUI:

    def __init__(self, root):
        self.root = root
        self.root.title("直播源接口更新工具")
        self.update_source = UpdateSource()
        self.update_running = False

    def save_config(self):
        source_file = self.source_file_entry.get()
        final_file = self.final_file_entry.get()
        favorite_list = self.favorite_list_text.get(1.0, tk.END)
        open_online_search = self.open_online_search_var.get()
        favorite_page_num = self.favorite_page_num_entry.get()
        default_page_num = self.default_page_num_entry.get()
        urls_limit = self.urls_limit_entry.get()
        open_sort = self.open_sort_var.get()
        response_time_weight = self.response_time_weight_entry.get()
        resolution_weight = self.resolution_weight_entry.get()
        recent_days = self.recent_days_entry.get()
        ipv_type = self.ipv_type_combo.get()
        domain_blacklist = self.domain_blacklist_text.get(1.0, tk.END)
        url_keywords_blacklist = self.url_keywords_blacklist_text.get(1.0, tk.END)
        open_subscribe = self.open_subscribe_var.get()
        subscribe_urls = self.subscribe_urls_text.get(1.0, tk.END)
        open_multicast = self.open_multicast_var.get()
        region_list = self.region_list_text.get(1.0, tk.END)

        config.source_file = source_file
        config.final_file = final_file
        config.favorite_list = favorite_list
        config.open_online_search = open_online_search
        config.favorite_page_num = favorite_page_num
        config.default_page_num = default_page_num
        config.urls_limit = urls_limit
        config.open_sort = open_sort
        config.response_time_weight = response_time_weight
        config.resolution_weight = resolution_weight
        config.recent_days = recent_days
        config.ipv_type = ipv_type
        config.domain_blacklist = domain_blacklist
        config.url_keywords_blacklist = url_keywords_blacklist
        config.open_subscribe = open_subscribe
        config.subscribe_urls = subscribe_urls
        config.open_multicast = open_multicast
        config.region_list = region_list
        user_config_file = (
            "user_config.py" if os.path.exists("user_config.py") else "config.py"
        )
        with open(user_config_file, "w") as f:
            f.write(f'source_file = "{source_file}"\n')
            f.write(f'final_file = "{final_file}"\n')
            f.write(f"favorite_list = {favorite_list}\n")
            f.write(f"open_online_search = {open_online_search}\n")
            f.write(f"favorite_page_num = {favorite_page_num}\n")
            f.write(f"default_page_num = {default_page_num}\n")
            f.write(f"urls_limit = {urls_limit}\n")
            f.write(f"open_sort = {open_sort}\n")
            f.write(f"response_time_weight = {response_time_weight}\n")
            f.write(f"resolution_weight = {resolution_weight}\n")
            f.write(f"recent_days = {recent_days}\n")
            f.write(f'ipv_type = "{ipv_type}"\n')
            f.write(f"domain_blacklist = {domain_blacklist}\n")
            f.write(f"url_keywords_blacklist = {url_keywords_blacklist}\n")
            f.write(f"open_subscribe = {open_subscribe}\n")
            f.write(f"subscribe_urls = {subscribe_urls}\n")
            f.write(f"open_multicast = {open_multicast}\n")
            f.write(f"region_list = {region_list}\n")
            messagebox.showinfo("提示", "保存成功")

    def run_update(self):
        self.update_running = not self.update_running
        if self.update_running:
            self.run_button.config(text="取消更新", state="normal")
            self.progress_bar["value"] = 0
            self.progress_label.pack()
            self.progress_bar.pack()
            self.update_source.start(self.update_progress)
        else:
            self.update_source.stop()
            self.run_button.config(text="开始更新", state="normal")
            self.progress_bar.pack_forget()
            self.progress_label.pack_forget()

    def update_progress(self, title, progress, finished=False):
        self.progress_bar["value"] = progress
        self.progress_label["text"] = f"{title}, 进度: {progress}%"
        self.root.update()
        if finished:
            self.run_button.config(text="开始更新", state="normal")

    def init_UI(self):

        row1 = tk.Frame(self.root)
        row1.pack(fill=tk.X)
        row1_column1 = tk.Frame(row1)
        row1_column1.pack(side=tk.LEFT, fill=tk.Y)
        row1_column2 = tk.Frame(row1)
        row1_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_subscribe_label = tk.Label(row1_column1, text="开启订阅源:", width=15)
        self.open_subscribe_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.open_subscribe_var = tk.BooleanVar(value=config.open_subscribe)
        self.open_subscribe_checkbutton = ttk.Checkbutton(
            row1_column1,
            width=12,
            variable=self.open_subscribe_var,
            onvalue=True,
            offvalue=False,
        )
        self.open_subscribe_checkbutton.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_multicast_label = tk.Label(row1_column2, text="开启组播源:", width=15)
        self.open_multicast_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.open_multicast_var = tk.BooleanVar(value=config.open_multicast)
        self.open_multicast_checkbutton = ttk.Checkbutton(
            row1_column2,
            width=12,
            variable=self.open_multicast_var,
            onvalue=True,
            offvalue=False,
        )
        self.open_multicast_checkbutton.pack(side=tk.LEFT, padx=5, pady=5)

        row2 = tk.Frame(self.root)
        row2.pack(fill=tk.X)
        row2_column1 = tk.Frame(row2)
        row2_column1.pack(side=tk.LEFT, fill=tk.Y)
        row2_column2 = tk.Frame(row2)
        row2_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.open_online_search_label = tk.Label(
            row2_column1, text="开启线上搜索:", width=15
        )
        self.open_online_search_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.open_online_search_var = tk.BooleanVar(value=config.open_online_search)
        self.open_online_search_checkbutton = ttk.Checkbutton(
            row2_column1,
            width=12,
            variable=self.open_online_search_var,
            onvalue=True,
            offvalue=False,
        )
        self.open_online_search_checkbutton.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_sort_label = tk.Label(row2_column2, text="开启测速排序:", width=15)
        self.open_sort_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.open_sort_var = tk.BooleanVar(value=config.open_sort)
        self.open_sort_checkbutton = ttk.Checkbutton(
            row2_column2,
            width=12,
            variable=self.open_sort_var,
            onvalue=True,
            offvalue=False,
        )
        self.open_sort_checkbutton.pack(side=tk.LEFT, padx=5, pady=5)

        row3 = tk.Frame(self.root)
        row3.pack(fill=tk.X)
        row3_column1 = tk.Frame(row3)
        row3_column1.pack(side=tk.LEFT, fill=tk.Y)
        row3_column2 = tk.Frame(row3)
        row3_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.source_file_label = tk.Label(row3_column1, text="模板文件:", width=15)
        self.source_file_entry = tk.Entry(row3_column1)
        self.source_file_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.source_file_entry.pack(fill=tk.X, padx=5, expand=True)
        self.source_file_entry.insert(0, config.source_file)

        self.final_file_label = tk.Label(row3_column2, text="结果文件:", width=15)
        self.final_file_entry = tk.Entry(row3_column2)
        self.final_file_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.final_file_entry.pack(fill=tk.X, padx=5, expand=True)
        self.final_file_entry.insert(0, config.final_file)

        row4 = tk.Frame(self.root)
        row4.pack(fill=tk.X)

        self.favorite_list_label = tk.Label(row4, text="关注频道:", width=15)
        self.favorite_list_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.favorite_list_scrollbar = tk.Scrollbar(row4, orient="vertical")
        self.favorite_list_text = scrolledtext.ScrolledText(
            row4,
            height=3,
            wrap=tk.WORD,
            yscrollcommand=self.favorite_list_scrollbar.set,
        )
        self.favorite_list_text.pack(
            side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH
        )
        self.favorite_list_text.insert(tk.END, config.favorite_list)
        self.favorite_list_scrollbar.config(command=self.favorite_list_text.yview)
        self.favorite_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row5 = tk.Frame(self.root)
        row5.pack(fill=tk.X)
        row5_column1 = tk.Frame(row5)
        row5_column1.pack(side=tk.LEFT, fill=tk.Y)
        row5_column2 = tk.Frame(row5)
        row5_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.favorite_page_num_label = tk.Label(
            row5_column1, text="关注获取页数:", width=15
        )
        self.favorite_page_num_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.favorite_page_num_entry = tk.Entry(row5_column1)
        self.favorite_page_num_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.favorite_page_num_entry.insert(0, config.favorite_page_num)

        self.default_page_num_label = tk.Label(
            row5_column2, text="默认获取页数:", width=15
        )
        self.default_page_num_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.default_page_num_entry = tk.Entry(row5_column2)
        self.default_page_num_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.default_page_num_entry.insert(0, config.default_page_num)

        row6 = tk.Frame(self.root)
        row6.pack(fill=tk.X)
        row6_column1 = tk.Frame(row6)
        row6_column1.pack(side=tk.LEFT, fill=tk.Y)
        row6_column2 = tk.Frame(row6)
        row6_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.urls_limit_label = tk.Label(
            row6_column1, text="单个频道接口数量:", width=15
        )
        self.urls_limit_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.urls_limit_entry = tk.Entry(row6_column1)
        self.urls_limit_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.urls_limit_entry.insert(15, config.urls_limit)

        self.ipv_type_label = tk.Label(row6_column2, text="接口协议类型:", width=15)
        self.ipv_type_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.ipv_type_combo = ttk.Combobox(row6_column2)
        self.ipv_type_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.ipv_type_combo["values"] = ("ipv4", "ipv6", "all")
        self.ipv_type_combo.current(0)
        self.ipv_type_combo.bind("<<ComboboxSelected>>", lambda event: config.ipv_type)

        row7 = tk.Frame(self.root)
        row7.pack(fill=tk.X)
        row7_column1 = tk.Frame(row7)
        row7_column1.pack(side=tk.LEFT, fill=tk.Y)
        row7_column2 = tk.Frame(row7)
        row7_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.response_time_weight_label = tk.Label(
            row7_column1, text="响应时间权重:", width=15
        )
        self.response_time_weight_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.response_time_weight_entry = tk.Entry(row7_column1)
        self.response_time_weight_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.response_time_weight_entry.insert(0, config.response_time_weight)

        self.resolution_weight_label = tk.Label(
            row7_column2, text="分辨率权重:", width=15
        )
        self.resolution_weight_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.resolution_weight_entry = tk.Entry(row7_column2)
        self.resolution_weight_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.resolution_weight_entry.insert(0, config.resolution_weight)

        row8 = tk.Frame(self.root)
        row8.pack(fill=tk.X)

        self.recent_days_label = tk.Label(row8, text="获取时间范围(天):", width=15)
        self.recent_days_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.recent_days_entry = tk.Entry(row8)
        self.recent_days_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.recent_days_entry.insert(30, config.recent_days)

        row9 = tk.Frame(self.root)
        row9.pack(fill=tk.X)

        self.domain_blacklist_label = tk.Label(row9, text="域名黑名单:", width=15)
        self.domain_blacklist_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.domain_blacklist_scrollbar = tk.Scrollbar(row9, orient="vertical")
        self.domain_blacklist_text = scrolledtext.ScrolledText(
            row9,
            height=3,
            wrap=tk.WORD,
            yscrollcommand=self.domain_blacklist_scrollbar.set,
        )
        self.domain_blacklist_text.pack(
            side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH
        )
        self.domain_blacklist_text.insert(tk.END, config.domain_blacklist)
        self.domain_blacklist_scrollbar.config(command=self.domain_blacklist_text.yview)
        self.domain_blacklist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row10 = tk.Frame(self.root)
        row10.pack(fill=tk.X)

        self.url_keywords_blacklist_label = tk.Label(
            row10, text="关键字黑名单:", width=15
        )
        self.url_keywords_blacklist_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.url_keywords_blacklist_scrollbar = tk.Scrollbar(row10, orient="vertical")
        self.url_keywords_blacklist_text = scrolledtext.ScrolledText(
            row10,
            height=3,
            wrap=tk.WORD,
            yscrollcommand=self.url_keywords_blacklist_scrollbar.set,
        )
        self.url_keywords_blacklist_text.pack(
            side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH
        )
        self.url_keywords_blacklist_text.insert(tk.END, config.url_keywords_blacklist)
        self.url_keywords_blacklist_scrollbar.config(
            command=self.url_keywords_blacklist_text.yview
        )
        self.url_keywords_blacklist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row11 = tk.Frame(self.root)
        row11.pack(fill=tk.X)

        self.subscribe_urls_label = tk.Label(row11, text="订阅源:", width=15)
        self.subscribe_urls_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.subscribe_urls_scrollbar = tk.Scrollbar(row11, orient="vertical")
        self.subscribe_urls_text = scrolledtext.ScrolledText(
            row11,
            height=3,
            wrap=tk.WORD,
            yscrollcommand=self.subscribe_urls_scrollbar.set,
        )
        self.subscribe_urls_text.pack(
            side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH
        )
        self.subscribe_urls_text.insert(tk.END, config.subscribe_urls)
        self.subscribe_urls_scrollbar.config(command=self.subscribe_urls_text.yview)
        self.subscribe_urls_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row12 = tk.Frame(self.root)
        row12.pack(fill=tk.X)

        self.region_list_label = tk.Label(row12, text="组播地区:", width=15)
        self.region_list_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.region_list_scrollbar = tk.Scrollbar(row12, orient="vertical")
        self.region_list_text = scrolledtext.ScrolledText(
            row12,
            height=3,
            wrap=tk.WORD,
            yscrollcommand=self.region_list_scrollbar.set,
        )
        self.region_list_text.pack(
            side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.BOTH
        )
        self.region_list_text.insert(tk.END, config.region_list)
        self.region_list_scrollbar.config(command=self.region_list_text.yview)
        self.region_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row13 = tk.Frame(self.root)
        row13.pack(fill=tk.X, pady=10, padx=120)
        row13_column1 = tk.Frame(row13)
        row13_column1.pack(side=tk.LEFT, fill=tk.Y)
        row13_column2 = tk.Frame(row13)
        row13_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.save_button = tk.Button(
            row13_column1, text="保存设置", command=self.save_config
        )
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.run_button = tk.Button(
            row13_column2, text="开始更新", command=self.run_update
        )
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)

        row14 = tk.Frame(self.root)
        row14.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(row14, length=200, mode="determinate")
        self.progress_bar.pack_forget()
        self.progress_label = tk.Label(row14, text="进度: 0%")
        self.progress_label.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_ui = TkinterUI(root)
    tkinter_ui.init_UI()
    root.geometry("500x600")
    root.mainloop()
