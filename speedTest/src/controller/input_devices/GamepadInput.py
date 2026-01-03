import threading
import time
import logging as log
from inputs import get_gamepad
from inputs import devices

from controller.input_devices.InputDevice import InputDevice

class GamepadInput(InputDevice):
    def __init__(self, input_controller, aspect_ratio: float):
        self.input_controller = input_controller

        # Current pointer coordinates normalized (0..1)
        self.pointer_x = 0.5
        self.pointer_y = 0.5

        # Last recorded stick position (-1..1)
        self.last_x = 0.0
        self.last_y = 0.0

        # Buttons
        self._button_pressed = False
        self._button_codes = {"BTN_SOUTH", "BTN_EAST", "BTN_NORTH", "BTN_WEST"}
        self._buttons_state = {code: False for code in self._button_codes}

        # Threading
        self._running = False
        self._event_thread = None
        self._update_thread = None
        self._lock = threading.Lock()

        # Parameters
        self.sensitivity = 0.05
        self.deadzone = 0.1
        self.update_interval = 0.05  # seconds
        self.aspect_ratio = aspect_ratio

    def _normalize(self, value):
        """Convert raw input -32768..32767 to -1..1"""
        return (2 * (value + 32768) / 65535) - 1

    def _apply_deadzone(self, value):
        """Ignore small stick movements inside the deadzone"""
        if abs(value) < self.deadzone:
            return 0.0
        return value

    def _event_loop(self):
        """Thread: reads gamepad events and stores the last stick values"""
        while self._running:
            events = get_gamepad()
            for event in events:
                if event.code == "ABS_X":
                    with self._lock:
                        self.last_x = self._apply_deadzone(self._normalize(event.state))
                elif event.code == "ABS_Y":
                    with self._lock:
                        self.last_y = self._apply_deadzone(self._normalize(event.state))
                elif event.code in self._button_codes:
                    self._handle_button_event(event.code, bool(event.state))


    def _handle_button_event(self, event_code, pressed: bool):
        """Update the button state and trigger click/release if needed"""
        with self._lock:
            # Update the pressed state of this button
            self._buttons_state[event_code] = pressed

            # Check if any button is currently pressed
            if any(self._buttons_state.values()):
                if not self._button_pressed:
                    self._button_pressed = True
                    self.input_controller.left_click(self.pointer_x, self.pointer_y)
            else:  # All buttons released
                if self._button_pressed:
                    self._button_pressed = False
                    self.input_controller.left_release(self.pointer_x, self.pointer_y)


    def _update_loop(self):
        """Thread: continuously updates the pointer position"""
        last_reported_pointer = (self.pointer_x, self.pointer_y)
        while self._running:
            with self._lock:
                move_x = self.last_x
                move_y = self.last_y

            # Move pointer
            self.pointer_x += move_x * self.sensitivity
            self.pointer_y -= move_y * self.sensitivity * self.aspect_ratio  # Y inverted

            # Clamp to 0..1
            self.pointer_x = max(0.0, min(1.0, self.pointer_x))
            self.pointer_y = max(0.0, min(1.0, self.pointer_y))

            # Only report if the position actually changed
            if (round(self.pointer_x, 4), round(self.pointer_y, 4)) != (
                round(last_reported_pointer[0], 4),
                round(last_reported_pointer[1], 4),
            ):
                self.input_controller.move_to(self.pointer_x, self.pointer_y)
                last_reported_pointer = (self.pointer_x, self.pointer_y)

            time.sleep(self.update_interval)

    def activate(self):
        """Starts the gamepad listener threads"""
        if self._running:
            return
        self._running = True
        self._event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._event_thread.start()
        self._update_thread.start()

    def deactivate(self):
        """Stops the gamepad listener threads"""
        self._running = False
        if self._event_thread:
            self._event_thread.join(timeout=1)
        if self._update_thread:
            self._update_thread.join(timeout=1)

    def gamepad_connected(self):
        if devices.gamepads:
            return True
        else:
            return False
        
    def get_name(self):
        return "Gamepad"
