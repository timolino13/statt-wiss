from __future__ import annotations
from typing import TYPE_CHECKING

import logging as log
import tkinter as tk

from controller.ContainsVisitor import ContainsVisitor
from controller.state.IdleState import IdleState
from controller.state.RunningState import RunningState
from controller.state.EditState import EditState

if TYPE_CHECKING:
    from pathlib import Path
    from view.View import View
    from model.Model import Model
    from controller.InputController import InputController


class Controller:
    """
    Handles the logic of the general flow of the application.
    Most logic is inside the state classes, shared logic between states is here.
    """

    def __init__(self, model: Model):
        self.model = model
        self._timer_job = None
        self.time_remaining = 0
        self.contains_visitor = ContainsVisitor()

        # late inits in main.py
        self.view: View = None 
        self.input_controller: InputController = None 

        # States, so they dont need to be newly created every time
        self.idle_state = IdleState(self)
        self.running_state = RunningState(self)
        self.edit_state = EditState(self)
        self.state = self.idle_state



    # ================== Configuration / Export ==================
    def _load_config(self, config_path: Path):
        """Load configuration from file and disable export button."""
        self.model.load_config(config_path)

    def _export_config(self, filepath: Path):
        self.model.export_config(filepath)

    def _export_log(self, filepath: Path, type: str):
        """Export click log to a JSON file."""
        if type == "json":
            self.model.export_click_log_json(filepath)
        elif type == "csv":
            self.model.export_click_log_csv(filepath)
        else:
            log.warning(f"unkown export type: {type}, defaulting to JSON.")
            self.model.export_click_log_json(filepath)