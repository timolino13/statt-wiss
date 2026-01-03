from __future__ import annotations
from typing import TYPE_CHECKING
import logging as log

from controller.state.State import State

if TYPE_CHECKING:
    from pathlib import Path



class IdleState(State):
    def on_enter(self):
        # set UI state
        view = self.controller.view
        view.input_dropdown.configure(state="normal")
        
        # Button
        view.stop_btn.configure(state="disabled")
        view.show_start_button()
        view.hide_stop_button()
        view.hide_edit_ui()

        # Menu
        view.config_menu.entryconfig("Edit Config", state="normal")
        view.config_menu.entryconfig("Load Config", state="normal")
        
        log.info("Entered idle state.")
        

    def canvas_left_click(self, x: int, y: int):
        """Checks if the start button was clicked."""
        view = self.controller.view
        if view.start_button_coords:
            x1, y1, x2, y2 = view.start_button_coords
            if x1 <= x <= x2 and y1 <= y <= y2:
                # start button hit
                self._start_test()


    def on_device_change(self, event):
        self.controller.input_controller.change_device(event.widget.get())

    def load_config(self, config_path: Path):
        self.controller._load_config(config_path)

    def export_log(self, filepath: Path, type: str):
        self.controller._export_log(filepath, type)

    def export_config(self, filepath: Path):
        self.controller._export_config(filepath)

    def edit_mode(self):
        """Switch to edit state"""
        self.controller.state = self.controller.edit_state
        self.controller.state.on_enter()

    def _start_test(self):
        # Check if there are shapes
        if not self.controller.model.shapes:
            log.warning("Cannot start test without shapes.")
            return

        self.controller.state = self.controller.running_state
        self.controller.state.on_enter()