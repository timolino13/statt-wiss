from __future__ import annotations
from typing import TYPE_CHECKING

import logging as log

from controller.state.State import State
from controller.UpdateVisitor import UpdateVisitor
from model.Model import DuplicateIDError

if TYPE_CHECKING:
    from model.shapes import Shape
    from pathlib import Path

class EditState(State):
    def on_enter(self):
        # set UI state
        view = self.controller.view

        # Force mouse input
        view.input_dropdown.current(0)
        view.input_dropdown.configure(state="disabled")
        self.controller.input_controller.change_device("Mouse")
        view.hide_start_button()

        # Buttons
        view.stop_btn.config(state="disabled")
        view.show_edit_ui()

        # Menu
        view.config_menu.entryconfig("Edit Config", state="disabled")
        view.config_menu.entryconfig("Load Config", state="normal")

        # Remembering shape and position for drag and drop
        self._dragged_shape = None
        self._dragged_offset_x = 0
        self._dragged_offset_y = 0
        
        log.info("Entered edit state.")

    def canvas_left_click(self, x: int, y: int):
        shape = self._check_shape_hit(x, y)
        if shape:
            self._dragged_shape = shape
            # Calculate offset (click pos - shape pos)
            self._dragged_offset_x = x - shape.x
            self._dragged_offset_y = y - shape.y

            
    def canvas_right_click(self, x: int, y: int):
        """Check if any shape was hit. If so, open dialog to edit.
        If not, open dialog to select new shape."""
        shape = self._check_shape_hit(x, y)
        if shape:
            self.controller.view.edit_shape_dialog(x, y, shape)
            return
        self.controller.view.new_shape_dialog(x, y)

    def _check_shape_hit(self, x: int, y: int) -> Shape|None:
        """Returns the first shape hit or None"""
        visitor = self.controller.contains_visitor
        for shape in self.controller.model.shapes:
            visitor.set_position(x, y)
            shape.accept(visitor)
            if visitor.result:
                return shape
        return None
    
    def canvas_motion(self, x: int, y: int):
        self._update_from_dnd(x, y, False) # No snapshot
    
    def canvas_left_release(self, x: int, y: int):
        self._update_from_dnd(x, y)
        self._dragged_shape = None
    
    def _update_from_dnd(self, x: int, y: int, snapshot=True):
        if self._dragged_shape:
            values = {"x": x - self._dragged_offset_x,
                      "y": y - self._dragged_offset_y}
            self.update_shape(values, shape=self._dragged_shape, snapshot=snapshot)

    def update_shape(self, values, shape, snapshot=True):
        visitor = UpdateVisitor(values)
        shape.accept(visitor)
        self.controller.model.notify() # calling notify here, as the visitor does not acces the model, but the shaped directly
        if snapshot:
            self.controller.model.snapshot() # snapshot AFTER change, current state is snapshot
        

    def set_timer_duration(self, duration):
        self.controller.model.set_timer_duration(duration)
        self.controller.model.snapshot() # snapshot after change

    def add_shape_from_dialog(self, values):
        try:
            self.controller.model.add_shape(values.pop("type"), **values)
            self.controller.model.snapshot() # snapshot after change
        except DuplicateIDError:
            self.controller.view.show_id_error(values["id"])

    def delete_shape(self, shape):
        self.controller.model.delete_shape(shape)
        self.controller.model.snapshot() # snapshot after change

    def load_config(self, config_path: Path):
        self.controller._load_config(config_path)

    def export_log(self, filepath: Path, type: str):
        self.controller._export_log(filepath, type)

    def export_config(self, filepath: Path):
        self.controller._export_config(filepath)

    def exit_edit_mode(self):
        self.controller.state = self.controller.idle_state
        self.controller.state.on_enter()

    def undo(self):
        self.controller.model.undo()

    def redo(self):
        self.controller.model.redo()