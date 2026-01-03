from model.shapes import *

class EditVisitor:
    """
    Visitor used by the view to create dicts for editing shapes on a Tkinter canvas.
    Includes color as editable field.
    """
    def __init__(self):
        self.result = None
    
    # ============== Square ============== #
    def visit_square(self, square: Square):
        self.result = {
            "x": {"type": int, "default": square.x},
            "y": {"type": int, "default": square.y},
            "size": {"type": int, "default": square.size},
            "color": {"type": str, "default": square.color}
        }

    # ============== Circle ============== #
    def visit_circle(self, circle: Circle):
        self.result = {
            "x": {"type": int, "default": circle.x},
            "y": {"type": int, "default": circle.y},
            "radius": {"type": int, "default": circle.radius},
            "color": {"type": str, "default": circle.color}
        }

    # ============== Rectangle ============== #
    def visit_rectangle(self, rectangle: Rectangle):
        self.result = {
            "x": {"type": int, "default": rectangle.x},
            "y": {"type": int, "default": rectangle.y},
            "width": {"type": int, "default": rectangle.width},
            "height": {"type": int, "default": rectangle.height},
            "color": {"type": str, "default": rectangle.color}
        }

    # ============== Triangle ============== #
    def visit_triangle(self, triangle: Triangle):
        self.result = {
            "x": {"type": int, "default": triangle.x},
            "y": {"type": int, "default": triangle.y},
            "size": {"type": int, "default": triangle.size},
            "color": {"type": str, "default": triangle.color}
        }

    # ============== Ellipse ============== #
    def visit_ellipse(self, ellipse: Ellipse):
        self.result = {
            "x": {"type": int, "default": ellipse.x},
            "y": {"type": int, "default": ellipse.y},
            "rx": {"type": int, "default": ellipse.rx},
            "ry": {"type": int, "default": ellipse.ry},
            "color": {"type": str, "default": ellipse.color}
        }
