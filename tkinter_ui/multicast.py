import tkinter as tk
from tkinter import ttk
from utils.config import config, resource_path
import json
from select_combobox import SelectCombobox


class MulticastUI:

    def init_ui(self, root):
        """
        Init multicast UI
        """
        frame_multicast_multicast = tk.Frame(root)
        frame_multicast_multicast.pack(fill=tk.X)

        self.open_multicast_label = tk.Label(
            frame_multicast_multicast, text="开启组播源:", width=9
        )
        self.open_multicast_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_multicast_var = tk.BooleanVar(
            value=config.getboolean("Settings", "open_multicast")
        )
        self.open_multicast_checkbutton = ttk.Checkbutton(
            frame_multicast_multicast,
            variable=self.open_multicast_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_multicast,
        )
        self.open_multicast_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_multicast_region_list = tk.Frame(root)
        frame_multicast_region_list.pack(fill=tk.X)

        self.region_list_label = tk.Label(
            frame_multicast_region_list, text="组播地区:", width=9
        )
        self.region_list_label.pack(side=tk.LEFT, padx=4, pady=8)
        with open(
            resource_path("updates/multicast/multicast_map.json"), "r", encoding="utf-8"
        ) as f:
            regions_obj = json.load(f)
            regions = list(regions_obj.keys())
        region_selected_values = [
            value
            for value in config.get("Settings", "multicast_region_list").split(",")
            if value.strip()
        ]
        self.region_list_combo = SelectCombobox(
            frame_multicast_region_list,
            values=regions,
            selected_values=region_selected_values,
            height=10,
        )
        self.region_list_combo.pack(
            side=tk.LEFT, padx=4, pady=8, expand=True, fill=tk.BOTH
        )
        self.region_list_combo.bind("<KeyRelease>", self.update_region_list)

        frame_multicast_page_num = tk.Frame(root)
        frame_multicast_page_num.pack(fill=tk.X)

        self.page_num_label = tk.Label(
            frame_multicast_page_num, text="获取页数:", width=9
        )
        self.page_num_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry = tk.Entry(frame_multicast_page_num)
        self.page_num_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry.insert(0, config.getint("Settings", "multicast_page_num"))
        self.page_num_entry.bind("<KeyRelease>", self.update_page_num)

    def update_open_multicast(self):
        config.set("Settings", "open_multicast", str(self.open_multicast_var.get()))

    def update_region_list(self, event):
        config.set(
            "Settings",
            "multicast_region_list",
            ",".join(self.region_list_combo.selected_values),
        )

    def update_page_num(self, event):
        config.set("Settings", "multicast_page_num", self.page_num_entry.get())

    def change_entry_state(self, state):
        for entry in [
            "open_multicast_checkbutton",
            "region_list_combo",
            "page_num_entry",
        ]:
            getattr(self, entry).config(state=state)
