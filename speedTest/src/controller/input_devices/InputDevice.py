from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.InputController import InputController


class InputDevice:
    def __init__(self, input_controller: InputController):
        self.input_controller = input_controller

    def activate(self):
        raise NotImplementedError

    def deactivate(self):
        raise NotImplementedError
    
    def get_name(self):
        return "No name set"