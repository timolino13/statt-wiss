from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from tkinter import ttk, filedialog as fd
from tkinter import messagebox
import logging as log
import os
from pathlib import Path
from inputs import devices

from paths import CONFIG_DIR, LOG_DIR
from view.DrawVisitor import DrawVisitor
from view.CanvasCursor import CanvasCursor
from view.EditVisitor import EditVisitor
from view.popups.EditDialog import EditDialog
from view.popups.NewShapeDialog import NewShapeDialog
from view.popups.TimerDialog import TimerDialog


if TYPE_CHECKING:
    from model.Model import Model
    from model.shapes import Shape
    from controller.Controller import Controller
    

class View:
    def __init__(self, root: tk.Tk, model: Model, controller: Controller):
        self.root = root
        self.model = model
        self.model.set_observer(self)
        self.controller = controller

        root.geometry("1000x800")

        # ================== Menubar ==================
        menubar = tk.Menu(root, bg='lightgray')
        root.config(menu=menubar)

        # File menu
        self.file_menu = tk.Menu(menubar, tearoff=0)

        # Submenu for export
        export_menu = tk.Menu(self.file_menu, tearoff=0)
        export_menu.add_command(label="JSON", command=self.choose_export_log_json)
        export_menu.add_command(label="CSV", command=self.choose_export_log_csv)

        self.file_menu.add_cascade(label="Export Clicks", menu=export_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Quit", command=self.quit_program)

        # Config menu
        self.config_menu = tk.Menu(menubar, tearoff=0)
        self.config_menu.add_command(label="Edit Config", command=lambda: controller.state.edit_mode())
        self.config_menu.add_separator()
        self.config_menu.add_command(label="Load Config", command=self.choose_config)
        self.config_menu.add_command(label="Export Config", command=self.choose_export_config)
        
        

        menubar.add_cascade(label="File", menu=self.file_menu)
        menubar.add_cascade(label="Config", menu=self.config_menu)


        # ================== Toolbar ==================
        toolbar = ttk.Frame(root)

        # Dropdow for input devices
        inputs = ["Mouse", "Hand Tracking"]
        if devices.gamepads:
            inputs.append("Gamepad")
            
        ttk.Label(toolbar, text="Input Device:").pack(side=tk.LEFT, padx=5)
        self.input_cb_var = tk.StringVar(value="Mouse")  # Default = "Mouse"
        self.input_dropdown = ttk.Combobox(
            toolbar,
            textvariable=self.input_cb_var,
            values=inputs,
            state="readonly",
            width=15
        )
        self.input_dropdown.pack(side="left", padx=5, pady=4)
        self.input_dropdown.bind(
            "<<ComboboxSelected>>",
            lambda event: controller.state.on_device_change(event)
        )

        # Dropdown with configs
        ttk.Label(toolbar, text="Configs:").pack(side=tk.LEFT, padx=5)
        self.config_files = [f.stem for f in CONFIG_DIR.glob("*.json")]
        self.config_var = tk.StringVar()
        self.config_combobox = ttk.Combobox(
            toolbar,
            textvariable=self.config_var,
            values=self.config_files,
            state="readonly",
            width=20
        )
        self.config_combobox.pack(side=tk.LEFT, padx=5)
        self.config_combobox.bind("<<ComboboxSelected>>", self.on_config_selected)
        if self.config_files:
            self.config_var.set(self.config_files[0])

        # stop button
        self.stop_btn = ttk.Button(
            toolbar,
            text="Stop",
            state='disabled',
            command=lambda: controller.state.stop_test()
        )

        # ================== Buttons for edit mode. Initially not visible ==================
        # Button to exit the editor
        self.exit_edit_btn = ttk.Button(
            toolbar,
            text="Exit Editor",
            state="disabled",
            command=lambda: controller.state.exit_edit_mode()
        )

        self.save_as_btn = ttk.Button(
            toolbar,
            text="Save As...",
            state="disabled",
            command=self.choose_export_config
        ) 
        
        # Button to edit timer duration
        self.edit_timer_btn = ttk.Button(
            toolbar,
            text="Edit Timer...",
            state="disabled",
            command=self.edit_timer_dialog
        )

        self.undo_btn = ttk.Button(
            toolbar,
            text="Undo",
            state="disabled",
            command=lambda: self.controller.state.undo()
        )

        self.redo_btn = ttk.Button(
            toolbar,
            text="Redo",
            state="disabled",
            command=lambda: self.controller.state.redo()
        )



        # ================== Timer ==================
        self.timer_label = ttk.Label(toolbar, text="Timer:")
        self.timer_label.pack(side=tk.RIGHT, padx=2, pady=2)


        toolbar.pack(side="top", fill="x")


        # ================== Canvas ==================
        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill="both", expand=True)
        self._create_canvas_start_button()
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.draw_visitor = DrawVisitor(self.canvas)
        self.cursor = CanvasCursor(self.canvas)

        # Display inital state
        self.update()
        self.update_timer()
        self._raise_start_button()


        # ================== Keybinds ==================
        root.bind("<Control-z>", lambda event: self.controller.state.undo())
        root.bind("<Control-y>", lambda event: self.controller.state.redo())
        root.bind("<Command-z>", lambda event: self.controller.state.undo())
        root.bind("<Shift-Command-z>", lambda event: self.controller.state.redo())


    # config selected from drop down
    def on_config_selected(self, event=None):
        selected_name = self.config_var.get()
        if not selected_name:
            return

        # Datei-Pfad zusammensetzen
        filepath = CONFIG_DIR / f"{selected_name}.json"

        # Config laden
        self.controller.state.load_config(filepath)


    def refresh_config_list(self):
        """Loads every confing inside /config into the dropdown."""
        current = self.config_var.get()
        configs = [f.stem for f in CONFIG_DIR.glob("*.json")]
        configs.sort()  # optional: alphabetisch sortieren

        self.config_combobox["values"] = configs

        # Beibehaltung der Auswahl, falls die Datei noch existiert
        if current in configs:
            self.config_var.set(current)
        elif configs:
            self.config_var.set(configs[0])
        else:
            self.config_var.set("")


    def _create_canvas_start_button(self):
        """Create start button once"""
        w, h = 200, 80
        # Startrechteck
        self.start_button_item = self.canvas.create_rectangle(
            0, 0, w, h,
            fill='lightgray', outline='black', width=3,
            tags="start_button"
        )
        # Starttext
        self.start_button_text_item = self.canvas.create_text(
            0, 0, text="START", font=("Arial", 24), fill="black",
            tags="start_button"
        )

    def _on_canvas_resize(self, event: tk.Event):
        """center start button on resize"""
        w, h = 200, 80
        cx, cy = event.width // 2, event.height // 2
        x1, y1 = cx - w//2, cy - h//2
        x2, y2 = cx + w//2, cy + h//2
        self.start_button_coords = (x1, y1, x2, y2)

        self.canvas.coords(self.start_button_item, x1, y1, x2, y2)
        self.canvas.coords(self.start_button_text_item, cx, cy)


    def _raise_start_button(self):
        if self.start_button_item:
            self.canvas.tag_raise(self.start_button_item)
        if self.start_button_text_item:
            self.canvas.tag_raise(self.start_button_text_item)

        # Make sure cursor is always in front
        self.cursor.raise_cursor()


    def update(self):
        self.canvas.delete('shape')  # Delete existing shapes, but not cursor or start button
        self.draw_visitor.active = self.model.shape_active
        for shape in self.model.shapes:
            shape.accept(self.draw_visitor)
        self.cursor.raise_cursor()
        self._raise_start_button()
        self._set_undo_redo_state()


    def update_timer(self, seconds: int=None):
        if seconds is None:
            seconds = self.model.timer_duration # Get from config if not specified
        self.timer_label.config(text=f"Timer {seconds}s")
        self._set_undo_redo_state()


    def _set_undo_redo_state(self):
        if self.controller.state == self.controller.edit_state:
            if len(self.model.undo_stack) > 1:
                self.undo_btn.config(state="enabled")
            else:
                self.undo_btn.config(state="disabled")

            if self.model.redo_stack:
                self.redo_btn.config(state="enabled")
            else:
                self.redo_btn.config(state="disabled")


    def quit_program(self):
        self.root.destroy()


    # ================== State dependant UI toggles ==================
    def show_start_button(self):
        """Make the start button visible (Button on Canvas)."""
        if self.start_button_item:
            self.canvas.itemconfigure(self.start_button_item, state='normal')
        if self.start_button_text_item:
            self.canvas.itemconfigure(self.start_button_text_item, state='normal')
        self._raise_start_button()

    def hide_start_button(self):
        """Hide the canvas start button. (Button on Canvas)"""
        if self.start_button_item:
            self.canvas.itemconfigure(self.start_button_item, state='hidden')
        if self.start_button_text_item:
            self.canvas.itemconfigure(self.start_button_text_item, state='hidden')

    def show_stop_button(self):
        self.stop_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.stop_btn.configure(state="enabled")

    def hide_stop_button(self):
        self.stop_btn.pack_forget()
        self.stop_btn.configure(state="disabled")

    def show_edit_ui(self):
        self.exit_edit_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.exit_edit_btn.configure(state="enabled")
        self.save_as_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.save_as_btn.configure(state="enabled")
        self.undo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.redo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        self.edit_timer_btn.pack(side=tk.RIGHT, padx=2, pady=2, after=self.timer_label)
        self.edit_timer_btn.configure(state="enabled")
        self.update() # to set state of undo / redo button
    
    def hide_edit_ui(self):
        self.exit_edit_btn.pack_forget()
        self.exit_edit_btn.configure(state="disabled")
        self.save_as_btn.pack_forget()
        self.save_as_btn.configure(state="disabled")
        self.edit_timer_btn.pack_forget()
        self.edit_timer_btn.configure(state="disabled")
        self.undo_btn.pack_forget()
        self.undo_btn.configure(state="disabled")
        self.redo_btn.pack_forget()
        self.redo_btn.configure(state="disabled")
        self.edit_timer_btn.pack_forget()
        self.edit_timer_btn.configure(state="disabled")

    
    # ================== Dialogs ==================
    def edit_shape_dialog(self, x: int, y: int, shape: Shape):
        visitor = EditVisitor()
        shape.accept(visitor)
        fields = visitor.result
        EditDialog(
            self.root,
            x=x,
            y=y,
            fields=fields, 
            callback_ok=lambda values: self.controller.state.update_shape(values, shape),
            callback_delete=lambda: self.controller.state.delete_shape(shape)
        )

    def edit_timer_dialog(self):
        TimerDialog(
            parent=self.root,
            callback=lambda duration: self.controller.state.set_timer_duration(duration),
            initial_value=self.model.timer_duration
        )

    def new_shape_dialog(self, x: int=0, y: int=0):
        from model.shapes import shape_classes
        NewShapeDialog(
            self.root,
            shape_classes,
            x=x,
            y=y,
            callback=lambda values: self.controller.state.add_shape_from_dialog(values)
        )

    def show_id_error(self, shape_id):
        """Shows a popup, that a given id is allready in use."""
        messagebox.showerror(
            title="Duplicate ID",
            message=f"The ID '{shape_id}' is already used. Please choose a unique ID.",
            parent=self.root
        )

    def choose_config(self):
        filepath = fd.askopenfilename(
            title="Select configuration file",
            initialdir=CONFIG_DIR,
            filetypes=[("JSON files", "*.json")]
        )

        if filepath:
            self.controller.state.load_config(Path(filepath))


    def choose_export_config(self):
        filepath = fd.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            initialdir=CONFIG_DIR,
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            path = Path(filepath)
            self.controller.state.export_config(path)
            self.refresh_config_list() # to update config drop-down
            self.config_var.set(path.stem)


    def choose_export_log_json(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        filepath = fd.asksaveasfilename(
            title="Save Click Log as JSON",
            defaultextension=".json",
            initialdir=LOG_DIR,
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            self.controller.state.export_log(Path(filepath), "json")

    
    def choose_export_log_csv(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        filepath = fd.asksaveasfilename(
            title="Save Click Log as CSV",
            defaultextension=".csv",
            initialdir=LOG_DIR,
            filetypes=[("CSV files", "*.csv")]
        )

        if filepath:
            self.controller.state.export_log(Path(filepath), "csv")


