from model.shapes import *

class ConfigVisitor:
    """
    Visitor that creates a dictionary representation of a Shape,
    suitable for saving to a JSON config.
    Uses x and y instead of pos.
    """
    def __init__(self):
        self.result = None

    def visit_square(self, square: Square):
        self.result = {
            "type": "square",
            "id": square.id,
            "x": square.x,
            "y": square.y,
            "color": square.color,
            "size": square.size
        }

    def visit_rectangle(self, rectangle: Rectangle):
        self.result = {
            "type": "rectangle",
            "id": rectangle.id,
            "x": rectangle.x,
            "y": rectangle.y,
            "color": rectangle.color,
            "width": rectangle.width,
            "height": rectangle.height
        }

    def visit_circle(self, circle: Circle):
        self.result = {
            "type": "circle",
            "id": circle.id,
            "x": circle.x,
            "y": circle.y,
            "color": circle.color,
            "radius": circle.radius
        }

    def visit_triangle(self, triangle: Triangle):
        self.result = {
            "type": "triangle",
            "id": triangle.id,
            "x": triangle.x,
            "y": triangle.y,
            "color": triangle.color,
            "size": triangle.size
        }

    def visit_ellipse(self, ellipse: Ellipse):
        self.result = {
            "type": "ellipse",
            "id": ellipse.id,
            "x": ellipse.x,
            "y": ellipse.y,
            "color": ellipse.color,
            "rx": ellipse.rx,
            "ry": ellipse.ry
        }
