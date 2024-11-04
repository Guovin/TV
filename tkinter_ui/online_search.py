import tkinter as tk
from tkinter import ttk
from utils.config import config


class OnlineSearchUI:
    def init_ui(self, root):
        """
        Init online search UI
        """

        frame_online_search_open_online_search = tk.Frame(root)
        frame_online_search_open_online_search.pack(fill=tk.X)

        self.open_online_search_label = tk.Label(
            frame_online_search_open_online_search, text="开启关键字搜索:", width=13
        )
        self.open_online_search_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_online_search_var = tk.BooleanVar(value=config.open_online_search)
        self.open_online_search_checkbutton = ttk.Checkbutton(
            frame_online_search_open_online_search,
            variable=self.open_online_search_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_online_search,
        )
        self.open_online_search_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_online_search_page_num = tk.Frame(root)
        frame_online_search_page_num.pack(fill=tk.X)

        self.page_num_label = tk.Label(
            frame_online_search_page_num, text="获取页数:", width=13
        )
        self.page_num_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry = tk.Entry(frame_online_search_page_num)
        self.page_num_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry.insert(0, config.online_search_page_num)
        self.page_num_entry.bind("<KeyRelease>", self.update_page_num)

        frame_online_search_recent_days = tk.Frame(root)
        frame_online_search_recent_days.pack(fill=tk.X)

        self.recent_days_label = tk.Label(
            frame_online_search_recent_days, text="获取时间范围(天):", width=13
        )
        self.recent_days_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.recent_days_entry = tk.Entry(frame_online_search_recent_days)
        self.recent_days_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.recent_days_entry.insert(30, config.recent_days)
        self.recent_days_entry.bind("<KeyRelease>", self.update_recent_days)

    def update_open_online_search(self):
        config.set(
            "Settings", "open_online_search", str(self.open_online_search_var.get())
        )

    def update_page_num(self, event):
        config.set("Settings", "online_search_page_num", self.page_num_entry.get())

    def update_recent_days(self, event):
        config.set("Settings", "recent_days", self.recent_days_entry.get())

    def change_entry_state(self, state):
        for entry in [
            "open_online_search_checkbutton",
            "page_num_entry",
            "recent_days_entry",
        ]:
            getattr(self, entry).config(state=state)
