from tkinter import ttk


class SelectCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        selected_values = kwargs.pop("selected_values", [])
        values = kwargs.pop("values", [])
        command = kwargs.pop("command", None)
        super().__init__(master, **kwargs)
        self.selected_values = selected_values
        self.values = values
        self.command = command
        self["values"] = self.values
        self.bind("<<ComboboxSelected>>", self.on_select)
        self.bind("<FocusOut>", self.on_text_change)
        self.update_values()

    def on_select(self, event):
        selected_value = self.get().strip()
        self.update_selected_values(selected_value)
        self.update_values()
        if self.command:
            self.command(event)

    def on_text_change(self, event):
        text_value = self.get().strip()
        value_list = [value.strip() for value in text_value.split(",") if value.strip()]
        self.selected_values = [
            value for value in self.selected_values if value in value_list
        ]
        for value in value_list:
            if value in self.values and value not in self.selected_values:
                self.selected_values.append(value)
        self.update_values()
        if self.command:
            self.command(event)

    def update_selected_values(self, value):
        if value in self.selected_values:
            self.selected_values.remove(value)
        else:
            self.selected_values.append(value)

    def update_values(self):
        display_text = ",".join(self.selected_values)
        self.set(display_text)
