from __future__ import annotations
from typing import TYPE_CHECKING

import logging as log

if TYPE_CHECKING:
    from tkinter import Event
    from controller.Controller import Controller
    from model.shapes import Shape
    from pathlib import Path


class State:
    def __init__(self, controller: Controller):
        self.controller = controller

    def on_enter():
        raise NotImplementedError

    def canvas_left_click(self, x: int, y: int):
        raise NotImplementedError
    
    def canvas_left_release(self, x: int, y: int):
        pass

    def canvas_motion(self, x: int, y: int):
        pass
    
    def canvas_right_click(self, x, y):
        log.info("Right click does nothing in this state.")
    
    def load_config(self, config_path):
        log.warning("Cannot load config in this state.")

    def stop_test(self):
        log.warning("Method not callable in this state.")

    def on_device_change(self, event: Event):
        log.warning("Device cannot be changed in this state.")

    def edit_mode(self):
        log.warning("Cannot enter edit mode in this state.")

    def exit_edit_mode(self):
        log.warning("Cannit exit edit mode when not in edit state.")

    def update_shape(self, values: dict, shape: Shape):
        log.warning("Cannot update shape in this state.")

    def set_timer_duration(self, duration: int):
        log.warning("Cannot edit timer duration in this state.")

    def add_shape_from_dialog(self, values: dict):
        log.warning("Cannot add a shape in this state.")

    def export_log(self, filepath: Path, type: str):
        log.warning("Cannot export click log in this state.")

    def export_config(self, filepath: Path):
        log.warning("Cannot export config in this state.")

    def delete_shape(self, shape: Shape):
        log.warning("Cannot delete a shape in this state.")

    def undo(self):
        log.warning("Cannot undo in this state")

    def redo(self):
        log.warning("Cannot redo in this state")