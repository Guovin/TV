import sys
import os

sys.path.append(os.path.dirname(sys.path[0]))
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from utils.config import config, resource_path
from main import UpdateSource
import asyncio
import threading
import webbrowser
from default import DefaultUI
from multicast import MulticastUI
from hotel import HotelUI
from subscribe import SubscribeUI
from online_search import OnlineSearchUI
import json


class TkinterUI:
    def __init__(self, root):
        with open(resource_path("version.json"), "r", encoding="utf-8") as f:
            info = json.load(f)
        self.root = root
        self.root.title(info.get("name", ""))
        self.version = info.get("version", "")
        self.default_ui = DefaultUI()
        self.multicast_ui = MulticastUI()
        self.hotel_ui = HotelUI()
        self.subscribe_ui = SubscribeUI()
        self.online_search_ui = OnlineSearchUI()
        self.update_source = UpdateSource()
        self.update_running = False
        self.config_entrys = [
            "open_update_checkbutton",
            "open_use_old_result_checkbutton",
            "open_driver_checkbutton",
            "open_proxy_checkbutton",
            "source_file_entry",
            "source_file_button",
            "final_file_entry",
            "final_file_button",
            "open_subscribe_checkbutton",
            "open_multicast_checkbutton",
            "open_online_search_checkbutton",
            "open_keep_all_checkbutton",
            "open_sort_checkbutton",
            "page_num_entry",
            "urls_limit_entry",
            "response_time_weight_entry",
            "resolution_weight_entry",
            "ipv_type_combo",
            "recent_days_entry",
            "domain_blacklist_text",
            "url_keywords_blacklist_text",
            "subscribe_urls_text",
            "region_list_combo",
        ]
        self.result_url = None

    def view_result_link_callback(self, event):
        webbrowser.open_new_tab(self.result_url)

    def save_config(self):
        config_values = {
            "open_update": self.default_ui.open_update_var.get(),
            "open_use_old_result": self.default_ui.open_use_old_result_var.get(),
            "source_file": self.default_ui.source_file_entry.get(),
            "final_file": self.default_ui.final_file_entry.get(),
            "urls_limit": self.default_ui.urls_limit_entry.get(),
            "open_driver": self.default_ui.open_driver_var.get(),
            "open_proxy": self.default_ui.open_proxy_var.get(),
            "open_keep_all": self.default_ui.open_keep_all_var.get(),
            "open_sort": self.default_ui.open_sort_var.get(),
            "response_time_weight": self.default_ui.response_time_weight_entry.get(),
            "resolution_weight": self.default_ui.resolution_weight_entry.get(),
            "ipv_type": self.default_ui.ipv_type_combo.get(),
            "domain_blacklist": self.default_ui.domain_blacklist_text.get(1.0, tk.END),
            "url_keywords_blacklist": self.default_ui.url_keywords_blacklist_text.get(
                1.0, tk.END
            ),
            "open_subscribe": self.subscribe_ui.open_subscribe_var.get(),
            "subscribe_urls": self.subscribe_ui.subscribe_urls_text.get(1.0, tk.END),
            "open_multicast": self.multicast_ui.open_multicast_var.get(),
            "region_list": self.multicast_ui.region_list_combo.get(),
            "open_online_search": self.online_search_ui.open_online_search_var.get(),
            "page_num": self.online_search_ui.page_num_entry.get(),
            "recent_days": self.online_search_ui.recent_days_entry.get(),
        }

        for key, value in config_values.items():
            config.set("Settings", key, str(value))
        user_config_file = "config/" + (
            "user_config.ini"
            if os.path.exists(resource_path("user_config.ini"))
            else "config.ini"
        )
        user_config_path = resource_path(user_config_file, persistent=True)
        os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
        with open(user_config_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)
        messagebox.showinfo("提示", "保存成功")

    async def run_update(self):
        self.update_running = not self.update_running
        if self.update_running:
            self.run_button.config(text="取消更新", state="normal")
            self.default_ui.change_entry_state(state="disabled")
            self.multicast_ui.change_entry_state(state="disabled")
            self.hotel_ui.change_entry_state(state="disabled")
            self.subscribe_ui.change_entry_state(state="disabled")
            self.online_search_ui.change_entry_state(state="disabled")
            self.progress_bar["value"] = 0
            self.progress_label.pack()
            self.view_result_link.pack()
            self.progress_bar.pack()
            await self.update_source.start(self.update_progress)
        else:
            self.stop()
            self.update_source.stop()
            self.run_button.config(text="开始更新", state="normal")
            self.default_ui.change_entry_state(state="normal")
            self.multicast_ui.change_entry_state(state="normal")
            self.hotel_ui.change_entry_state(state="normal")
            self.subscribe_ui.change_entry_state(state="normal")
            self.online_search_ui.change_entry_state(state="normal")
            self.progress_bar.pack_forget()
            self.view_result_link.pack_forget()
            self.progress_label.pack_forget()

    def on_run_update(self):
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_update())

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        asyncio.get_event_loop().stop()

    def update_progress(self, title, progress, finished=False, url=None):
        self.progress_bar["value"] = progress
        progress_text = f"{title}, 进度: {progress}%" if not finished else f"{title}"
        self.progress_label["text"] = progress_text
        self.root.update()
        if finished:
            self.run_button.config(text="开始更新", state="normal")
            self.update_running = False
            for entry in self.config_entrys:
                getattr(self, entry).config(state="normal")
            if url:
                self.view_result_link.config(text=url)
                self.result_url = url

    def init_UI(self):

        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=0)

        frame_default = ttk.Frame(notebook, width=500, height=500)
        frame_multicast = ttk.Frame(notebook, width=500, height=500)
        frame_hotel = ttk.Frame(notebook, width=500, height=500)
        frame_subscribe = ttk.Frame(notebook, width=500, height=500)
        frame_online_search = ttk.Frame(notebook, width=500, height=500)

        notebook.add(frame_default, text="通用设置")
        notebook.add(frame_multicast, text="组播源")
        notebook.add(frame_hotel, text="酒店源")
        notebook.add(frame_subscribe, text="订阅源")
        notebook.add(frame_online_search, text="在线搜索")

        self.default_ui.init_ui(frame_default)
        self.multicast_ui.init_ui(frame_multicast)
        self.hotel_ui.init_ui(frame_hotel)
        self.subscribe_ui.init_ui(frame_subscribe)
        self.online_search_ui.init_ui(frame_online_search)

        root_operate = tk.Frame(self.root)
        root_operate.pack(fill=tk.X, pady=8, padx=120)
        root_operate_column1 = tk.Frame(root_operate)
        root_operate_column1.pack(side=tk.LEFT, fill=tk.Y)
        root_operate_column2 = tk.Frame(root_operate)
        root_operate_column2.pack(side=tk.RIGHT, fill=tk.Y)

        self.save_button = tk.Button(
            root_operate_column1, text="保存设置", command=self.save_config
        )
        self.save_button.pack(side=tk.LEFT, padx=4, pady=8)

        self.run_button = tk.Button(
            root_operate_column2, text="开始更新", command=self.on_run_update
        )
        self.run_button.pack(side=tk.LEFT, padx=4, pady=8)

        version_frame = tk.Frame(self.root)
        version_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.version_label = tk.Label(
            version_frame, text=self.version, fg="gray", anchor="se"
        )
        self.version_label.pack(side=tk.RIGHT, padx=5, pady=5)

        self.author_label = tk.Label(
            version_frame,
            text="by Govin",
            fg="gray",
            anchor="se",
        )
        self.author_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.project_link = tk.Label(
            version_frame, text="访问项目主页", fg="blue", cursor="hand2"
        )
        self.project_link.pack(side=tk.LEFT, padx=5, pady=5)
        self.project_link.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new_tab("https://github.com/Guovin/TV"),
        )

        root_progress = tk.Frame(self.root)
        root_progress.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(
            root_progress, length=300, mode="determinate"
        )
        self.progress_bar.pack_forget()
        self.progress_label = tk.Label(root_progress, text="进度: 0%")
        self.progress_label.pack_forget()
        self.view_result_link = tk.Label(
            root_progress, text="", fg="blue", cursor="hand2"
        )
        self.view_result_link.bind(
            "<Button-1>",
            self.view_result_link_callback,
        )
        self.view_result_link.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_ui = TkinterUI(root)
    tkinter_ui.init_UI()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = 550
    height = 700
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry("%dx%d+%d+%d" % (width, height, x, y))
    root.mainloop()
