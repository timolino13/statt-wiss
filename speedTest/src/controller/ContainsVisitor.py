from model.shapes import *

class ContainsVisitor:
    """
    Visitor to check whether a given point (px, py) lies inside a shape.
    x, y of each shape is interpreted as the top-left of the bounding box.
    """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.result = False

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    # ============== Square ============== #
    def visit_square(self, square: Square):
        x0, y0 = square.x, square.y
        self.result = (x0 <= self.x <= x0 + square.size
                       and y0 <= self.y <= y0 + square.size)

    # ============== Circle ============== #
    def visit_circle(self, circle: Circle):
        # x, y = top-left of bounding box
        x0, y0 = circle.x, circle.y
        r = circle.radius
        cx = x0 + r
        cy = y0 + r
        dx = self.x - cx
        dy = self.y - cy
        self.result = dx * dx + dy * dy <= r ** 2

    # ============== Rectangle ============== #
    def visit_rectangle(self, rect: Rectangle):
        x0, y0 = rect.x, rect.y
        self.result = (x0 <= self.x <= x0 + rect.width
                       and y0 <= self.y <= y0 + rect.height)

    # ============== Triangle ============== #
    def visit_triangle(self, tri: Triangle):
        x0, y0 = tri.x, tri.y
        x1, y1 = x0, y0 + tri.size
        x2, y2 = x0 + tri.size, y0 + tri.size
        x3, y3 = x0 + tri.size / 2, y0

        denom = ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
        if denom == 0:
            self.result = False
            return

        a = ((y2 - y3) * (self.x - x3) + (x3 - x2) * (self.y - y3)) / denom
        b = ((y3 - y1) * (self.x - x3) + (x1 - x3) * (self.y - y3)) / denom
        c = 1 - a - b
        self.result = (0 <= a <= 1) and (0 <= b <= 1) and (0 <= c <= 1)

    # ============== Ellipse ============== #
    def visit_ellipse(self, ellipse: Ellipse):
        # x, y = top-left of bounding box
        x0, y0 = ellipse.x, ellipse.y
        rx, ry = ellipse.rx, ellipse.ry
        # transform to ellipse center
        cx = x0 + rx
        cy = y0 + ry
        dx = self.x - cx
        dy = self.y - cy
        self.result = (dx**2)/(rx**2) + (dy**2)/(ry**2) <= 1
