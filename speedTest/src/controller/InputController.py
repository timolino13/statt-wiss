from __future__ import annotations
from typing import TYPE_CHECKING

import logging as log

from controller.input_devices.MouseInput import MouseInput
from controller.input_devices.GamepadInput import GamepadInput

try:
    GESTURE_AVAILABLE = True
    from controller.input_devices.GestureInput import GestureInput
except:
    GESTURE_AVAILABLE = False

if TYPE_CHECKING:
    from view.View import View
    from controller.Controller import Controller

class InputController:
    """
    Main interface for input devices. Handles all logic regarding inputs.
    Expects normalized coordinates (0..1) and converts them to absolute pixel values
    before forwarding to CanvasCursor and AppController.
    """

    def __init__(self, controller:Controller, view: View):
        self.cursor = view.cursor
        self.canvas = view.canvas # for mouse input
        self.controller = controller

        # Default input device
        self.input_device = MouseInput(view.canvas, self)
        self.input_device.activate()


    def _to_pixels(self, x: float, y: float):
        """Convert normalized coordinates (0..1) to pixel coordinates."""
        canvas_width = self.cursor.canvas.winfo_width()
        canvas_height = self.cursor.canvas.winfo_height()
        px = int(x * canvas_width)
        py = int(y * canvas_height)
        return px, py
    

    def move_to(self, x: float, y: float):
        """Move cursor to position given in normalized coordinates."""
        px, py = self._to_pixels(x, y)
        self.cursor.move_to(px, py)
        self.controller.state.canvas_motion(px, py)


    def left_click(self, x: float, y: float):
        """Register left click at normalized coordinates."""
        px, py = self._to_pixels(x, y)
        self.controller.state.canvas_left_click(px, py)
        self.cursor.left_click()


    def left_release(self, x: float, y: float):
        """Register left release at normalized coordinates."""
        px, py = self._to_pixels(x, y)
        self.controller.state.canvas_left_release(px, py)
        self.cursor.left_release()


    def right_click(self, x: float, y: float):
        """Register right click at normalized coordinates."""
        px, py = self._to_pixels(x, y)
        self.controller.state.canvas_right_click(px, py)


    def change_device(self, device_name:str):
        """Deactivates the current input device, then activates the new one."""

        # Deactivate existing device
        if self.input_device:
            self.input_device.deactivate()

        # Setting new device
        if device_name == "Mouse":
            self.input_device = MouseInput(self.canvas, self)
        elif device_name == "Hand Tracking":
            if GESTURE_AVAILABLE:
                self.input_device = GestureInput(self)
            else:
                log.error("Error loading GesureInput.")
        elif device_name == "Gamepad":
            aspect_ratio = self.canvas.winfo_width() / self.canvas.winfo_height()
            self.input_device = GamepadInput(self, aspect_ratio)
        else:
            raise ValueError(f"Unknown input device: {device_name}")

        # Activate new device
        self.input_device.activate()
        log.info(f"Input device activated: {self.input_device.get_name()}")
