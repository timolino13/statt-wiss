import json
import csv
import time
import logging as log
import copy
from pathlib import Path

from paths import CONFIG_DIR, LOG_DIR
from model.shapes import *
from model.ConfigVisitor import ConfigVisitor

class Model:
    def __init__(self):
        self.observers = []

        self.timer_duration = 0
        self.undo_stack = []
        self.redo_stack = []

        self.shapes: list[Shape] = []
        
        self.shape_active: Shape = None
        self.click_log: list[dict] = []



    def next_shape(self):
        """Activates the next shape in the list (or first shape if no shape is active)."""
        if not self.shapes:
            return None

        if self.shape_active not in self.shapes:
            self.shape_active = self.shapes[0]
        else:
            idx = self.shapes.index(self.shape_active)
            self.shape_active = self.shapes[(idx + 1) % len(self.shapes)]
        self.notify()


    def register_click(self, hit: bool, x, y):
        """Registers a click for later export."""
        timestamp = time.time()
        shape_id = self.shape_active.id
        entry = {
            'timestamp': timestamp,
            'target_id': shape_id,
            'x': x,
            'y': y,
            'shape_hit': hit
        }
        self.click_log.append(entry)


    def export_click_log_json(self, path: Path=None):
        if path is None:
            path = LOG_DIR / "click_log.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w") as file:
            json.dump(self.click_log, file, indent=4)
        log.info(f"Click log exported to {path}")

    
    def export_click_log_csv(self, path: Path=None):
        """Exports the click log as CSV. Adds config_name to each row if provided."""
        if path is None:
            path = LOG_DIR / "click_log.csv"
        path.parent.mkdir(parents=True, exist_ok=True)

        # csv columns
        fieldnames = ['timestamp', 'target_id', 'x', 'y', 'shape_hit']

        with open(path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for click in self.click_log:
                row = {
                    'timestamp': click['timestamp'],
                    'target_id': click['target_id'],
                    'x': click['x'],
                    'y': click['y'],
                    'shape_hit': click['shape_hit']
                }
                writer.writerow(row)
        log.info(f'Click log exported to {path}')


    def export_config(self, path: Path = None):
        """Speichert die aktuelle Konfiguration als JSON-Datei."""
        if path is None:
            path = CONFIG_DIR / "click_log.json"

        all_shapes_config = []
        for shape in self.shapes:
            visitor = ConfigVisitor()
            shape.accept(visitor)
            all_shapes_config.append(visitor.result)

        config = {
            "timer_duration": self.timer_duration,
            "shapes": all_shapes_config
        }

        with open(path, "w") as f:
            json.dump(config, f, indent=4)

        log.info(f"Configuration saved to {path}")
        


    def set_no_active_shape(self):
        self.shape_active = None
        self.notify()
    
    def clear_log(self):
        self.click_log = []

    def set_observer(self, observer):
        self.observers.append(observer)

    def notify(self):
        """Used to notify observers when something about the shapes changed."""
        for obs in self.observers:
            obs.update()

    def notify_timer(self):
        """used to notify observers when timer duration changed"""
        for obs in self.observers:
            log.debug(f"observer {obs} update_timer() called.")
            obs.update_timer()

    def notify_all(self):
        self.notify()
        self.notify_timer()



    def load_config(self, config_path: Path):
        if not config_path.exists():
            log.warning(f"file {config_path.name} does not exist in {config_path.parent}. Use 'Config -> Load Config' to search your file system.")
            return
        
        with open(config_path) as file:
            config = json.load(file)

        # load duration
        duration = config.get("timer_duration")
        if duration is None:
            log.warning("Configuration does not include the 'timer_duration' key, assuming default value of 10s")
            self.timer_duration = 10

        elif not isinstance(duration, (int, float)):
            log.error(f"Invalid type for 'timer_duration': expected number, got {type(duration).__name__}")
            self.timer_duration = 10

        else:
            self.timer_duration = duration

        # load shapes
        shapes = config.get('shapes', None)
        if shapes is None:
            log.error("Configuration does not include the 'shapes' key, keeping previous config.")
            return 
        elif not shapes:
            log.warning("The 'shapes' key exists, but no shapes are defined.")

        self.shapes = [] #clear previous config

        for shape_data in config['shapes']:     
            if shape_data['color'] == 'lightgreen':
                log.warning('Using lightgreen for a shape is not recomended, as this is the color used for highlighting')

            shape_type = shape_data.pop("type")
            self.add_shape(shape_type, **shape_data)

        self.notify_timer()
        self.clear_undo_redo()
        self.snapshot() # snapshot of initial state
        log.info(f"Configuration '{config_path.stem}' loaded.")


    def add_shape(self, shape_type: str, **kwargs):
        if shape_type not in shape_classes:
            raise ValueError(f"Unknown shape type: {shape_type}")

        shape_id = kwargs.get("id")
        if not shape_id:
            raise MissingIDError("Shape ID must be provided")

        if any(s.id == shape_id for s in self.shapes):
            raise DuplicateIDError(f"Duplicate shape id '{shape_id}'")

        cls = shape_classes[shape_type]
        shape = cls(**kwargs)
        self.shapes.append(shape)
        self.notify()
        return shape

    def delete_shape(self, shape: Shape):
        self.shapes.remove(shape)
        self.notify()

    def set_timer_duration(self, duration):
        if isinstance(duration, (int, float)):
            self.timer_duration = duration
            self.notify_timer()
            log.info(f"Timer set to {duration}s")
        else:
            raise ValueError()
        

    # Memento would be overkill, so funcionality for undo / redo is here.
    def snapshot(self):
        snapshot = {"shapes": copy.deepcopy(self.shapes), "timer": self.timer_duration}
        log.debug(f"Snapshot")
        self.undo_stack.append(snapshot)
        self.redo_stack.clear()
        self.notify_all() # notify to update undo / redo button correctly


    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop()) # current state to redo
            state = self.undo_stack[-1] # get last state, but dont pop

            self.shapes = copy.deepcopy(state["shapes"])
            self.timer_duration = state["timer"]
            self.notify_all()
            log.debug("Undo.")
        else:
            log.info("Nothing to undo.")


    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state) # back on undo

            self.shapes = copy.deepcopy(state["shapes"])
            self.timer_duration = state["timer"]
            self.notify_all()
            log.debug("Redo.")
        else:
            log.info("Nothing to redo.")


    def clear_undo_redo(self):
        self.undo_stack.clear()
        self.redo_stack.clear()


            

# Errors raised in Model
class ShapeError(Exception):
    """Basis-Klasse für Shape-Fehler"""
    pass

class DuplicateIDError(ShapeError):
    """ID wird schon verwendet"""
    pass

class MissingIDError(ShapeError):
    """Keine ID angegeben"""
    pass