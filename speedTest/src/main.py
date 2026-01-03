# /// script
# requires-python = "==3.12.12"
# dependencies = [
#     "inputs",
#     "mediapipe",
#     "opencv-python",
# ]
# ///

import tkinter as tk
import logging

from model.Model import Model
from controller.Controller import Controller
from controller.InputController import InputController
from view.View import View

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

root = tk.Tk()

# MVC setup
model = Model()
controller = Controller(model)
view = View(root, model, controller)
input_controller = InputController(controller, view)


# late init for things that interact with the controller and view
controller.view = view
controller.input_controller = input_controller
controller.state.on_enter() # This references controller.view
view.on_config_selected() # load first config in folder. Needs the controller.

# start of main loop
root.mainloop()
