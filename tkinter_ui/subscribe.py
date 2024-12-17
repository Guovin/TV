import os
import os.path
import tkinter as tk
from tkinter import ttk

import utils.constants as constants
from utils.config import config
from utils.tools import resource_path


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
        frame_subscribe_urls_column1 = tk.Frame(frame_subscribe_subscribe_urls)
        frame_subscribe_urls_column1.pack(side=tk.LEFT, fill=tk.Y)
        frame_subscribe_urls_column2 = tk.Frame(frame_subscribe_subscribe_urls)
        frame_subscribe_urls_column2.pack(side=tk.LEFT, fill=tk.Y)

        self.subscribe_urls_label = tk.Label(
            frame_subscribe_urls_column1, text="订阅源:", width=9
        )
        self.subscribe_urls_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.subscribe_file_button = tk.ttk.Button(
            frame_subscribe_urls_column2,
            text="编辑",
            command=self.edit_subscribe_file,
        )
        self.subscribe_file_button.pack(side=tk.LEFT, padx=4, pady=0)

    def update_open_subscribe(self):
        config.set("Settings", "open_subscribe", str(self.open_subscribe_var.get()))

    def edit_subscribe_file(self):
        path = resource_path(constants.subscribe_path)
        if os.path.exists(path):
            os.system(f'notepad.exe {path}')

    def change_entry_state(self, state):
        for entry in [
            "open_subscribe_checkbutton",
            "subscribe_file_button",
        ]:
            getattr(self, entry).config(state=state)
