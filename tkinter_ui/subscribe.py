import tkinter as tk
from tkinter import ttk
from utils.config import config
from tkinter import scrolledtext


class SubscribeUI:
    def init_ui(self, root):
        """
        Init subscribe UI
        """
        frame_subscribe_open_subscribe = tk.Frame(root)
        frame_subscribe_open_subscribe.pack(fill=tk.X)

        self.open_subscribe_label = tk.Label(
            frame_subscribe_open_subscribe, text="开启订阅源:", width=9
        )
        self.open_subscribe_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_subscribe_var = tk.BooleanVar(value=config.open_subscribe)
        self.open_subscribe_checkbutton = ttk.Checkbutton(
            frame_subscribe_open_subscribe,
            variable=self.open_subscribe_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_subscribe,
        )
        self.open_subscribe_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_subscribe_subscribe_urls = tk.Frame(root)
        frame_subscribe_subscribe_urls.pack(fill=tk.X)

        self.subscribe_urls_label = tk.Label(
            frame_subscribe_subscribe_urls, text="订阅源:", width=9
        )
        self.subscribe_urls_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.subscribe_urls_text = scrolledtext.ScrolledText(
            frame_subscribe_subscribe_urls, height=40
        )
        self.subscribe_urls_text.pack(
            side=tk.LEFT, padx=4, pady=8, expand=True, fill=tk.BOTH
        )
        self.subscribe_urls_text.insert(tk.END, ",".join(config.subscribe_urls))
        self.subscribe_urls_text.bind("<KeyRelease>", self.update_subscribe_urls)

    def update_open_subscribe(self):
        config.set("Settings", "open_subscribe", str(self.open_subscribe_var.get()))

    def update_subscribe_urls(self, event):
        config.set(
            "Settings",
            "subscribe_urls",
            self.subscribe_urls_text.get(1.0, tk.END),
        )

    def change_entry_state(self, state):
        for entry in [
            "open_subscribe_checkbutton",
            "subscribe_urls_text",
        ]:
            getattr(self, entry).config(state=state)
