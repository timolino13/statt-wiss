import tkinter as tk
from tkinter import ttk, messagebox

class NewShapeDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, shape_classes: dict, x: int=0, y: int=0, callback=None):
        super().__init__(parent)
        self.title("New Shape")
        self.callback = callback
        self.result = None
        self.x = x
        self.y = y

        # Get parent position, move the popup near the click
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        self.geometry(f"+{parent_x + x}+{parent_y + y + 25}") # +25 for the toolbar

        self.bind("<Return>", lambda event: self.ok()) 
        self.bind("<Escape>", lambda event: self.cancel())

        # Shape-Auswahl
        tk.Label(self, text="Select shape type:").pack(pady=(10,2))
        self.var_type = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self, textvariable=self.var_type,
            values=list(shape_classes.keys()),
            state="readonly"
        )
        self.dropdown.pack(padx=5, pady=2)
        self.dropdown.current(0)

        # ID-Eingabe
        tk.Label(self, text="Enter shape ID:").pack(pady=(10,2))
        self.var_id = tk.StringVar()
        self.entry_id = tk.Entry(self, textvariable=self.var_id)
        self.entry_id.pack(padx=5, pady=2)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="OK", command=self.ok).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)

        self.focus_set()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)



    def ok(self):
        shape_id = self.var_id.get().strip()
        if not shape_id:
            tk.messagebox.showerror("Invalid ID", "ID cannot be empty!")
            return  # Dialog bleibt offen

        self.result = {
            "type": self.var_type.get(),
            "id": shape_id,
            "x": self.x,
            "y": self.y
        }
        if self.callback:
            self.callback(self.result)
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()
