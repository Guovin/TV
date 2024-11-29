import sys
import os

sys.path.append(os.path.dirname(sys.path[0]))
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.config import config
from utils.tools import resource_path
from main import UpdateSource
import asyncio
import threading
import webbrowser
from about import AboutUI
from default import DefaultUI
from prefer import PreferUI
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
        self.about_ui = AboutUI()
        self.default_ui = DefaultUI()
        self.prefer_ui = PreferUI()
        self.multicast_ui = MulticastUI()
        self.hotel_ui = HotelUI()
        self.subscribe_ui = SubscribeUI()
        self.online_search_ui = OnlineSearchUI()
        self.update_source = UpdateSource()
        self.update_running = False
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
            "open_filter_resolution": self.default_ui.open_filter_resolution_var.get(),
            "min_resolution": self.default_ui.min_resolution_entry.get(),
            "response_time_weight": self.default_ui.response_time_weight_scale.get(),
            "resolution_weight": self.default_ui.resolution_weight_scale.get(),
            "ipv_type": self.default_ui.ipv_type_combo.get(),
            "url_keywords_blacklist": self.default_ui.url_keywords_blacklist_text.get(
                1.0, tk.END
            ),
            "open_subscribe": self.subscribe_ui.open_subscribe_var.get(),
            "subscribe_urls": self.subscribe_ui.subscribe_urls_text.get(1.0, tk.END),
            "open_multicast": self.multicast_ui.open_multicast_var.get(),
            "open_multicast_foodie": self.multicast_ui.open_multicast_foodie_var.get(),
            "open_multicast_fofa": self.multicast_ui.open_multicast_fofa_var.get(),
            "multicast_region_list": self.multicast_ui.region_list_combo.get(),
            "multicast_page_num": self.multicast_ui.page_num_entry.get(),
            "open_hotel": self.hotel_ui.open_hotel_var.get(),
            "open_hotel_foodie": self.hotel_ui.open_hotel_foodie_var.get(),
            "open_hotel_fofa": self.hotel_ui.open_hotel_fofa_var.get(),
            "hotel_region_list": self.hotel_ui.region_list_combo.get(),
            "hotel_page_num": self.hotel_ui.page_num_entry.get(),
            "open_online_search": self.online_search_ui.open_online_search_var.get(),
            "online_search_page_num": self.online_search_ui.page_num_entry.get(),
            "recent_days": self.online_search_ui.recent_days_entry.get(),
            "open_update_time": self.default_ui.open_update_time_var.get(),
        }

        for key, value in config_values.items():
            config.set("Settings", key, str(value))
        config.save()
        messagebox.showinfo("提示", "保存成功")

    def change_state(self, state):
        self.default_ui.change_entry_state(state=state)
        self.prefer_ui.change_entry_state(state=state)
        self.multicast_ui.change_entry_state(state=state)
        self.hotel_ui.change_entry_state(state=state)
        self.subscribe_ui.change_entry_state(state=state)
        self.online_search_ui.change_entry_state(state=state)

    async def run_update(self):
        self.update_running = not self.update_running
        if self.update_running:
            self.run_button.config(text="取消更新", state="normal")
            self.change_state("disabled")
            self.progress_bar["value"] = 0
            self.progress_label.pack()
            self.view_result_link.pack()
            self.progress_bar.pack()
            await self.update_source.start(self.update_progress)
        else:
            self.stop()
            self.update_source.stop()
            self.run_button.config(text="开始更新", state="normal")
            self.change_state("normal")
            self.progress_bar.pack_forget()
            self.view_result_link.pack_forget()
            self.progress_label.pack_forget()

    def on_run_update(self):
        loop = asyncio.new_event_loop()

        def run_loop():
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
            self.change_state("normal")
            if url:
                self.view_result_link.config(text=url)
                self.result_url = url

    def init_UI(self):

        menu_bar = tk.Menu(self.root)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="关于",
            command=lambda: self.about_ui.init_ui(root=self.root, version=self.version),
        )
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menu_bar)

        notebook = tk.ttk.Notebook(self.root)
        notebook.pack(fill="both", padx=10, pady=5)

        frame_default = tk.ttk.Frame(notebook)
        frame_prefer = tk.ttk.Frame(notebook)
        frame_hotel = tk.ttk.Frame(notebook)
        frame_multicast = tk.ttk.Frame(notebook)
        frame_subscribe = tk.ttk.Frame(notebook)
        frame_online_search = tk.ttk.Frame(notebook)

        settings_icon_source = Image.open(
            resource_path("static/images/settings_icon.png")
        ).resize((16, 16))
        settings_icon = ImageTk.PhotoImage(settings_icon_source)
        prefer_icon_source = Image.open(
            resource_path("static/images/prefer_icon.png")
        ).resize((16, 16))
        prefer_icon = ImageTk.PhotoImage(prefer_icon_source)
        hotel_icon_source = Image.open(
            resource_path("static/images/hotel_icon.png")
        ).resize((16, 16))
        hotel_icon = ImageTk.PhotoImage(hotel_icon_source)
        multicast_icon_source = Image.open(
            resource_path("static/images/multicast_icon.png")
        ).resize((16, 16))
        multicast_icon = ImageTk.PhotoImage(multicast_icon_source)
        subscribe_icon_source = Image.open(
            resource_path("static/images/subscribe_icon.png")
        ).resize((16, 16))
        subscribe_icon = ImageTk.PhotoImage(subscribe_icon_source)
        online_search_icon_source = Image.open(
            resource_path("static/images/online_search_icon.png")
        ).resize((16, 16))
        online_search_icon = ImageTk.PhotoImage(online_search_icon_source)

        notebook.add(
            frame_default, text="通用设置", image=settings_icon, compound=tk.LEFT
        )
        notebook.add(frame_prefer, text="偏好设置", image=prefer_icon, compound=tk.LEFT)
        notebook.add(frame_hotel, text="酒店源", image=hotel_icon, compound=tk.LEFT)
        notebook.add(
            frame_multicast, text="组播源", image=multicast_icon, compound=tk.LEFT
        )
        notebook.add(
            frame_subscribe, text="订阅源", image=subscribe_icon, compound=tk.LEFT
        )
        notebook.add(
            frame_online_search,
            text="关键字搜索",
            image=online_search_icon,
            compound=tk.LEFT,
        )

        notebook.settings_icon = settings_icon
        notebook.prefer_icon = prefer_icon
        notebook.hotel_icon = hotel_icon
        notebook.multicast_icon = multicast_icon
        notebook.subscribe_icon = subscribe_icon
        notebook.online_search_icon = online_search_icon

        self.default_ui.init_ui(frame_default)
        self.prefer_ui.init_ui(frame_prefer)
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

        self.save_button = tk.ttk.Button(
            root_operate_column1, text="保存设置", command=self.save_config
        )
        self.save_button.pack(side=tk.LEFT, padx=4, pady=8)

        self.run_button = tk.ttk.Button(
            root_operate_column2, text="开始更新", command=self.on_run_update
        )
        self.run_button.pack(side=tk.LEFT, padx=4, pady=8)

        root_progress = tk.Frame(self.root)
        root_progress.pack(fill=tk.X)

        self.progress_bar = tk.ttk.Progressbar(
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


def get_root_location(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = 550
    height = 750
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    return (width, height, x, y)


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_ui = TkinterUI(root)
    tkinter_ui.init_UI()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry("%dx%d+%d+%d" % get_root_location(root))
    root.iconbitmap(resource_path("static/images/favicon.ico"))
    root.after(0, config.copy)
    root.mainloop()
