import tkinter as tk
from tkinter import ttk

class EditDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, x: int, y: int, fields: dict[str, dict], callback_ok=None, callback_delete=None):
        super().__init__(parent)
        self.parent = parent
        self.fields = fields   # dict: {field_name: {type: ..., default: ...}}
        self.entries = {}
        self.result = None
        self.callback_ok = callback_ok
        self.callback_delete = callback_delete

        
        # Get parent position, move the popup near the click
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        self.geometry(f"+{parent_x + x}+{parent_y + y + 25}") # +25 for the toolbar

        # Keybord shortcuts
        self.bind("<Return>", lambda event: self.ok()) 
        self.bind("<Escape>", lambda event: self.destroy())


        self.title("Edit Shape")

        for i, (field, info) in enumerate(fields.items()):
            ftype = info.get("type", str)
            default = info.get("default", "")

            tk.Label(self, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="w")

            # Validation command einrichten
            vcmd = (self.register(self._validate), "%P", "%V", ftype.__name__)
            entry = tk.Entry(self, validate="key", validatecommand=vcmd)
            entry.grid(row=i, column=1, padx=5, pady=5)

            if default != "":
                entry.insert(0, str(default))

            self.entries[field] = (entry, ftype)

            self.focus_set()


        # Custom Style for delete button
        style = ttk.Style()
        style.configure("Danger.TButton", background="#ff0000", foreground="black")

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        btn_apply = ttk.Button(button_frame, text="Apply", command=self.apply)
        btn_apply.pack(side="left", padx=3)

        btn_ok = ttk.Button(button_frame, text="OK", command=self.ok)
        btn_ok.pack(side="left", padx=3)

        btn_del = ttk.Button(button_frame, text="Delete", style="Danger.TButton", command=self.delete)
        btn_del.pack(side="left", padx=3)

        # Kein Cancel-Button, Fenster kann nur per OK geschlossen werden
        self.protocol("WM_DELETE_WINDOW", self.ok)
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)


    def _validate(self, proposed, reason, typename):
        """Validation function for entry fields"""
        if reason != "key":
            return True
        if typename == "str":
            return True
        elif typename == "int":
            if proposed == "" or (proposed.isdigit() or (proposed.startswith("-") and proposed[1:].isdigit())):
                return True
            return False
        elif typename == "float":
            if proposed == "":
                return True
            try:
                float(proposed)
                return True
            except ValueError:
                return False
        return True

    def get_values(self):
        values = {}
        for field, (entry, ftype) in self.entries.items():
            val = entry.get()
            if val == "":
                values[field] = None
            else:
                try:
                    values[field] = ftype(val)
                except ValueError:
                    values[field] = val  # fallback
        return values

    def apply(self):
        values = self.get_values()
        if self.callback_ok:
            self.callback_ok(values)

    def ok(self):
        self.result = self.get_values()
        if self.callback_ok:
            self.callback_ok(self.result)
        self.destroy()

    def delete(self):
        if self.callback_delete:
            self.callback_delete()
        self.destroy()
