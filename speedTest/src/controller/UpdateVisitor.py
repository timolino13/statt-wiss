from dataclasses import fields
from model.shapes import *

class UpdateVisitor:
    """
    Visitor that updates any dataclass-based shape's attributes from a dict of values.
    Only updates keys that exist in values.
    Works for x/y position and any other attributes (size, color, etc.).
    """
    def __init__(self, values: dict):
        self.values = values

    def _update_shape(self, shape):
        for f in fields(shape):
            if f.name in self.values:
                setattr(shape, f.name, self.values[f.name])

    # Visitor methods
    def visit_square(self, square: Square):
        self._update_shape(square)

    def visit_circle(self, circle: Circle):
        self._update_shape(circle)

    def visit_rectangle(self, rectangle: Rectangle):
        self._update_shape(rectangle)

    def visit_triangle(self, triangle: Triangle):
        self._update_shape(triangle)

    def visit_ellipse(self, ellipse: Ellipse):
        self._update_shape(ellipse)
