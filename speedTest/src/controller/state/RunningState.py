import logging as log
from typing import TYPE_CHECKING

from controller.state.State import State



class RunningState(State):
    def __init__(self, controller):
        super().__init__(controller)
        self._timer_job = None

    def on_enter(self):
        # Set ui state
        view = self.controller.view
        view.input_dropdown.configure(state="disabled")
        view.hide_start_button()
        view.show_stop_button()

        view.config_menu.entryconfig("Edit Config", state="disabled")
        view.config_menu.entryconfig("Load Config", state="disabled")
        
        
        # Start test
        model = self.controller.model
        model.clear_log()
        model.next_shape()
        self._start_timer(model.timer_duration)

        log.info("Entered RunningState.")


    def canvas_left_click(self, x: int, y: int):
        """Checks if the active shape was clicked and recording the click in the model."""
        self.controller.contains_visitor.set_position(x, y)
        self.controller.model.shape_active.accept(self.controller.contains_visitor)
        if self.controller.contains_visitor.result:
            log.debug("Active shape clicked.")
            self.controller.model.register_click(True, x, y)
            self.controller.model.next_shape()
        else:
            log.debug("Active shape missed.")
            self.controller.model.register_click(False, x, y)


    def stop_test(self):
        self._stop_timer()
        self.controller.model.set_no_active_shape()
        self.controller.state = self.controller.idle_state
        self.controller.state.on_enter()



    # ================== Timer ==================
    def _start_timer(self, duration: int):
        """Start the countdown timer."""
        self.time_remaining = duration
        self._tick()

    def _tick(self):
        """Update the timer each second and stop the task when it reaches zero."""
        if self.time_remaining <= 0:
            self.stop_test()
            return

        view = self.controller.view
        view.update_timer(self.time_remaining)
        self.time_remaining -= 1
        self._timer_job = view.root.after(1000, self._tick) # Call this method in 1s

    def _stop_timer(self):
        """Stop the countdown timer."""
        view = self.controller.view

        if self._timer_job:
            view.root.after_cancel(self._timer_job)
            self._timer_job = None
        view.update_timer(self.controller.model.timer_duration)
