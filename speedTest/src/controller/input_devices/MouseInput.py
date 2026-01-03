from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter as tk
from controller.input_devices.InputDevice import InputDevice

if TYPE_CHECKING:
    from controller.InputController import InputController


class MouseInput(InputDevice):
    def __init__(self, canvas: tk.Canvas, input_controller: InputController):
        super().__init__(input_controller)
        self.canvas = canvas
        self._motion_event = '<Motion>'
        self._left_click_event = '<Button-1>'
        self._left_release_event = '<ButtonRelease-1>'
        self._right_click_event = '<Button-3>'

    def activate(self):
        self.canvas.bind(self._motion_event, self._on_motion)
        self.canvas.bind(self._left_click_event, self._on_left_click)
        self.canvas.bind(self._left_release_event, self._on_left_release)
        self.canvas.bind(self._right_click_event, self._on_right_click)

    def deactivate(self):
        self.canvas.unbind(self._motion_event)
        self.canvas.unbind(self._left_click_event)
        self.canvas.unbind(self._left_release_event)

    def _normalize(self, x, y):
        """Convert absolute canvas coordinates to normalized (0..1)."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        nx = x / width if width > 0 else 0
        ny = y / height if height > 0 else 0
        return nx, ny

    def _on_motion(self, event):
        nx, ny = self._normalize(event.x, event.y)
        self.input_controller.move_to(nx, ny)

    def _on_left_click(self, event):
        nx, ny = self._normalize(event.x, event.y)
        self.input_controller.left_click(nx, ny)

    def _on_left_release(self, event):
        nx, ny = self._normalize(event.x, event.y)
        self.input_controller.left_release(nx, ny)

    def _on_right_click(self, event):
        nx, ny = self._normalize(event.x, event.y)
        self.input_controller.right_click(nx, ny)

    def get_name(self):
        return "Mouse"