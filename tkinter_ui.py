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


class TkinterUI:

    def __init__(self, root):
        self.root = root
        self.root.title("直播源接口更新工具")
        self.update_source = UpdateSource()
        self.update_running = False
        self.progress_thread = None

    def save_config():
        messagebox.showinfo("Info", "保存成功")

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

    def open_online_search_change_dropdown(self):
        config.open_online_search = self.open_online_search_combo.get()

    def update_progress(self, title, progress, finished=False):
        self.progress_bar["value"] = progress
        self.progress_label["text"] = f"{title}, 进度: {progress}%"
        self.root.update()
        if finished:
            self.run_button.config(text="开始更新", state="normal")

    def init_UI(self):
        source_file_label = tk.Label(self.root, text="模板文件")
        source_file_entry = tk.Entry(self.root)
        source_file_label.pack()
        source_file_entry.pack()
        source_file_entry.insert(0, config.source_file)

        final_file_label = tk.Label(self.root, text="结果文件")
        final_file_entry = tk.Entry(self.root)
        final_file_label.pack()
        final_file_entry.pack()
        final_file_entry.insert(0, config.final_file)

        favorite_list_label = tk.Label(self.root, text="关注频道")
        favorite_list_label.pack()
        scrollbar = tk.Scrollbar(self.root, orient="vertical")
        text = scrolledtext.ScrolledText(
            self.root, width=40, height=10, wrap=tk.WORD, yscrollcommand=scrollbar.set
        )
        text.pack(side=tk.LEFT, expand=True)
        text.insert(tk.END, config.favorite_list)

        scrollbar.config(command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        open_online_search_label = tk.Label(self.root, text="线上搜索")
        open_online_search_label.pack()
        open_online_search_combo = ttk.Combobox(self.root, width=12)
        open_online_search_combo.pack()

        open_online_search_combo["values"] = (True, False)
        open_online_search_combo.current(0)
        open_online_search_combo.bind(
            "<<ComboboxSelected>>", self.open_online_search_change_dropdown
        )

        save_button = tk.Button(self.root, text="保存设置", command=self.save_config)
        save_button.pack()

        self.run_button = tk.Button(self.root, text="开始更新", command=self.run_update)
        self.run_button.pack()

        self.progress_bar = ttk.Progressbar(self.root, length=200, mode="determinate")
        self.progress_bar.pack_forget()
        self.progress_label = tk.Label(self.root, text="进度: 0%")
        self.progress_label.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    tkinter_ui = TkinterUI(root)
    tkinter_ui.init_UI()
    root.geometry("700x400")
    root.mainloop()
