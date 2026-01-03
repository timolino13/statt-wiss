import tkinter as tk
import logging as log

class CanvasCursor:
    def __init__(self, canvas: tk.Canvas, radius: int = 7, color: str = 'yellow'):
        self.canvas = canvas
        self.radius = radius
        self.color = color
        self.color_pressed = 'red'
        self.item = None  # Canvas Item ID
        self.create()


    def create(self):
        # used to create the cursor.
        r = self.radius
        if self.item is None:
            self.item = self.canvas.create_oval(50-r, 50-r, 50+r, 50+r, fill=self.color, outline='black', width=2)

        # put cursor to front
        self.canvas.tag_raise(self.item)


    def move_to(self, x, y):
        if self.item is not None:
            # Nur die Position aktualisieren
            r = self.radius
            self.canvas.coords(self.item, x-r, y-r, x+r, y+r)
            

    def raise_cursor(self):
        if self.item is not None:
            self.canvas.tag_raise(self.item)

    
    def left_click(self):
        if self.item is not None:
            self.canvas.itemconfig(self.item, fill=self.color_pressed)

    def left_release(self):
        if self.item is not None:
            self.canvas.itemconfig(self.item, fill=self.color)