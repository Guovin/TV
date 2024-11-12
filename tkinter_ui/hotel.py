import tkinter as tk
from tkinter import ttk
from utils.config import config
from select_combobox import SelectCombobox
import updates.fofa.fofa_map as fofa_map


class HotelUI:
    def init_ui(self, root):
        """
        Init hotel UI
        """
        frame_hotel_open_hotel = tk.Frame(root)
        frame_hotel_open_hotel.pack(fill=tk.X)

        self.open_hotel_label = tk.Label(
            frame_hotel_open_hotel, text="开启酒店源:", width=9
        )
        self.open_hotel_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_hotel_var = tk.BooleanVar(value=config.open_hotel)
        self.open_hotel_checkbutton = ttk.Checkbutton(
            frame_hotel_open_hotel,
            variable=self.open_hotel_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_hotel,
        )
        self.open_hotel_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_hotel_mode = tk.Frame(root)
        frame_hotel_mode.pack(fill=tk.X)

        self.open_hotel_mode_label = tk.Label(
            frame_hotel_mode, text="工作模式:", width=9
        )
        self.open_hotel_mode_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.open_hotel_foodie_var = tk.BooleanVar(value=config.open_hotel_foodie)
        self.open_hotel_foodie_checkbutton = ttk.Checkbutton(
            frame_hotel_mode,
            variable=self.open_hotel_foodie_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_hotel_foodie,
            text="Foodie",
        )
        self.open_hotel_foodie_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        self.open_hotel_fofa_var = tk.BooleanVar(value=config.open_hotel_fofa)
        self.open_hotel_fofa_checkbutton = ttk.Checkbutton(
            frame_hotel_mode,
            variable=self.open_hotel_fofa_var,
            onvalue=True,
            offvalue=False,
            command=self.update_open_hotel_fofa,
            text="FOFA",
        )
        self.open_hotel_fofa_checkbutton.pack(side=tk.LEFT, padx=4, pady=8)

        frame_hotel_region_list = tk.Frame(root)
        frame_hotel_region_list.pack(fill=tk.X)

        self.region_list_label = tk.Label(
            frame_hotel_region_list, text="酒店地区:", width=9
        )
        self.region_list_label.pack(side=tk.LEFT, padx=4, pady=8)
        regions = ["全部"] + list(getattr(fofa_map, "region_url").keys())
        self.region_list_combo = SelectCombobox(
            frame_hotel_region_list,
            values=regions,
            selected_values=config.hotel_region_list,
            height=10,
            command=self.update_region_list,
        )
        self.region_list_combo.pack(
            side=tk.LEFT, padx=4, pady=8, expand=True, fill=tk.BOTH
        )

        frame_hotel_page_num = tk.Frame(root)
        frame_hotel_page_num.pack(fill=tk.X)

        self.page_num_label = tk.Label(frame_hotel_page_num, text="获取页数:", width=9)
        self.page_num_label.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry = tk.Entry(frame_hotel_page_num)
        self.page_num_entry.pack(side=tk.LEFT, padx=4, pady=8)
        self.page_num_entry.insert(0, config.hotel_page_num)
        self.page_num_entry.bind("<KeyRelease>", self.update_page_num)

    def update_open_hotel(self):
        config.set("Settings", "open_hotel", str(self.open_hotel_var.get()))

    def update_open_hotel_foodie(self):
        config.set(
            "Settings", "open_hotel_foodie", str(self.open_hotel_foodie_var.get())
        )

    def update_open_hotel_fofa(self):
        config.set("Settings", "open_hotel_fofa", str(self.open_hotel_fofa_var.get()))

    def update_region_list(self, event):
        config.set(
            "Settings",
            "hotel_region_list",
            ",".join(self.region_list_combo.selected_values),
        )

    def update_page_num(self, event):
        config.set("Settings", "hotel_page_num", self.page_num_entry.get())

    def change_entry_state(self, state):
        for entry in [
            "open_hotel_checkbutton",
            "open_hotel_foodie_checkbutton",
            "open_hotel_fofa_checkbutton",
            "region_list_combo",
            "page_num_entry",
        ]:
            getattr(self, entry).config(state=state)
