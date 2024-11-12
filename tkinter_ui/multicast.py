import tkinter as tk
from tkinter import ttk
from utils.tools import resource_path
from utils.config import config
from select_combobox import SelectCombobox
import os


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
        self.open_multicast_var = tk.BooleanVar(value=config.open_multicast)
        self.open_multicast_checkbutton = ttk.Checkbutton(
            frame_multicast_multicast,
            variable=self.open_multicast_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_multicast,
        )
        self.open_multicast_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_multicast_mode = tk.Frame(root)
        frame_multicast_mode.pack(fill=tk.X)

        self.open_multicast_mode_label = tk.Label(
            frame_multicast_mode, text="工作模式:", width=9
        )
        self.open_multicast_mode_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_multicast_foodie_var = tk.BooleanVar(
            value=config.open_multicast_foodie
        )
        self.open_multicast_foodie_checkbutton = ttk.Checkbutton(
            frame_multicast_mode,
            variable=self.open_multicast_foodie_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_multicast_foodie,
            text="Foodie",
        )
        self.open_multicast_foodie_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_multicast_fofa_var = tk.BooleanVar(value=config.open_multicast_fofa)
        self.open_multicast_fofa_checkbutton = ttk.Checkbutton(
            frame_multicast_mode,
            variable=self.open_multicast_fofa_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_multicast_fofa,
            text="FOFA",
        )
        self.open_multicast_fofa_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_multicast_region_list = tk.Frame(root)
        frame_multicast_region_list.pack(fill=tk.X)

        frame_multicast_region_list = tk.Frame(root)
        frame_multicast_region_list.pack(fill=tk.X)

        self.region_list_label = tk.Label(
            frame_multicast_region_list, text="组播地区:", width=9
        )
        self.region_list_label.pack(side=tk.LEFT, padx=4, pady=8)
        rtp_path = resource_path("config/rtp")
        regions = list(
            {"全部"}.union(
                filename.rsplit(".", 1)[0].partition("_")[0]
                for filename in os.listdir(rtp_path)
                if filename.endswith(".txt") and "_" in filename
            )
        )
        if "全部" in regions:
            regions.remove("全部")
        regions.insert(0, "全部")
        self.region_list_combo = SelectCombobox(
            frame_multicast_region_list,
            values=regions,
            selected_values=config.multicast_region_list,
            height=10,
            command=self.update_region_list,
        )
        self.region_list_combo.pack(
            side=tk.LEFT, padx=4, pady=8, expand=True, fill=tk.BOTH
        )

        frame_multicast_page_num = tk.Frame(root)
        frame_multicast_page_num.pack(fill=tk.X)

        self.page_num_label = tk.Label(
            frame_multicast_page_num, text="获取页数:", width=9
        )
        self.page_num_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry = tk.Entry(frame_multicast_page_num)
        self.page_num_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry.insert(0, config.multicast_page_num)
        self.page_num_entry.bind("<KeyRelease>", self.update_page_num)

    def update_open_multicast(self):
        config.set("Settings", "open_multicast", str(self.open_multicast_var.get()))

    def update_open_multicast_foodie(self):
        config.set(
            "Settings",
            "open_multicast_foodie",
            str(self.open_multicast_foodie_var.get()),
        )

    def update_open_multicast_fofa(self):
        config.set(
            "Settings", "open_multicast_fofa", str(self.open_multicast_fofa_var.get())
        )

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
            "open_multicast_foodie_checkbutton",
            "open_multicast_fofa_checkbutton",
            "region_list_combo",
            "page_num_entry",
        ]:
            getattr(self, entry).config(state=state)
