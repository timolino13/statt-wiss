import tkinter as tk
from tkinter import ttk, messagebox

class TimerDialog(tk.Toplevel):
    def __init__(self, parent, callback=None, initial_value=10):
        super().__init__(parent)
        self.title("Set Timer Duration")
        self.callback = callback
        self.result = None

        self.bind("<Return>", lambda event: self.ok()) 
        self.bind("<Escape>", lambda event: self.destroy())

        # Eingabe Label + Entry
        tk.Label(self, text="Enter duration (seconds):").pack(pady=(10, 5))

        vcmd = (self.register(self.only_numbers), "%P")
        self.var = tk.StringVar(value=str(initial_value))
        self.entry = ttk.Entry(
            self, textvariable=self.var,
            validate="key", validatecommand=vcmd
        )
        self.entry.pack(padx=10, pady=5)
        self.entry.focus()

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side="left", padx=5)

        self.update_idletasks()  # Größe des Fensters berechnen lassen
        self.center_window(parent)

        self.focus_set()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
        

    def only_numbers(self, P):
        return P.isdigit() or P == ""

    def ok(self):
        val = self.var.get()
        if val.isdigit() and int(val) > 0:
            self.result = int(val)
            if self.callback:
                self.callback(self.result)
            self.destroy()
        else:
            messagebox.showerror("Invalid input", "Please enter a positive number.")

    def cancel(self):
        self.result = None
        self.destroy()


    def center_window(self, parent):
        """Platziert das Dialogfenster mittig über dem Elternfenster"""
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        w = self.winfo_width()
        h = self.winfo_height()

        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)

        self.geometry(f"+{x}+{y}")
