from tkinter import ttk


class SelectCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        selected_values = kwargs.pop("selected_values", [])
        values = kwargs.pop("values", [])
        super().__init__(master, **kwargs)
        self.selected_values = selected_values
        self.values = values
        self["values"] = self.values
        self.bind("<<ComboboxSelected>>", self.on_select)
        self.update_values()

    def on_select(self, event):
        selected_value = self.get().strip()
        if selected_value in self.selected_values:
            self.selected_values.remove(selected_value)
        else:
            self.selected_values.append(selected_value)
        self.update_values()

    def update_values(self):
        display_text = ",".join(self.selected_values)
        self.set(display_text)
