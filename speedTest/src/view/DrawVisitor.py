from model.shapes import *
import tkinter as tk
import logging as log

class DrawVisitor:
    """
    Visitor used by the view to paint the shapes on a Tkinter canvas.
    """
    def __init__(self, canvas: tk.Canvas, active: Shape = None):
        self.canvas = canvas
        self.active = active  # Shape, das gerade hervorgehoben ist

    def _fill_color(self, shape: Shape):
        color = shape.color_active if shape is self.active else shape.color

        # Trying to convertg color (just a string in shape) to rgb, to see if its legal.
        # If not, use black.
        try:
            self.canvas.winfo_rgb(color) # return not needed, just check if it raises an error
            return color
        except tk.TclError:
            log.warning(f"color not legal: {color}. Using black.")
            return "black"

    
    # ============== Square ============== #
    def visit_square(self, square: Square):
        x = square.x
        y = square.y
        self.canvas.create_rectangle(
            x, y, x + square.size, y + square.size,
            fill=self._fill_color(square),
            outline='black',
            width=3 if square is self.active else 1,
            tags='shape'
        )

    # ============== Circle ============== #
    def visit_circle(self, circle: Circle):
        x = circle.x
        y = circle.y
        r = circle.radius
        self.canvas.create_oval(
            x, y, x + 2*r, y + 2*r,
            fill=self._fill_color(circle),
            outline='black',
            width=3 if circle is self.active else 1,
            tags='shape'
        )

    # ============== Rectangle ============== #
    def visit_rectangle(self, rect: Rectangle):
        x = rect.x
        y = rect.y
        self.canvas.create_rectangle(
            x, y, x + rect.width, y + rect.height,
            fill=self._fill_color(rect),
            outline='black',
            width=3 if rect is self.active else 1,
            tags='shape'
        )

    # ============== Triangle ============== #
    def visit_triangle(self, triangle: Triangle):
        x = triangle.x
        y = triangle.y
        points = [
            x, y + triangle.size, 
            x + triangle.size, y + triangle.size,
            x + triangle.size / 2, y
        ]
        self.canvas.create_polygon(
            points,
            fill=self._fill_color(triangle),
            outline='black',
            width=3 if triangle is self.active else 1,
            tags='shape'
        )

    # ============== Ellipse ============== #
    def visit_ellipse(self, ellipse: Ellipse):
        x = ellipse.x
        y = ellipse.y
        self.canvas.create_oval(
            x, y,
            x + 2*ellipse.rx, y + 2*ellipse.ry,
            fill=self._fill_color(ellipse),
            outline='black',
            width=3 if ellipse is self.active else 1,
            tags='shape'
        )
