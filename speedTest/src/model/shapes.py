from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Shape(ABC):
    id: str
    x: 0
    y: 0
    color: str = "gray"
    color_active = "lightgreen" # color used to highlight this shape

    @abstractmethod
    def accept(self, visitor):
        pass


@dataclass
class Square(Shape):
    size: int = 100
    
    def accept(self, visitor):
        visitor.visit_square(self)



@dataclass
class Circle(Shape):
    radius: int = 50
    
    def accept(self, visitor):
        visitor.visit_circle(self)

    

@dataclass
class Rectangle(Shape):
    width: int = 150
    height: int = 75
    
    def accept(self, visitor):
        visitor.visit_rectangle(self)



@dataclass
class Triangle(Shape):
    size: int = 100
    
    def accept(self, visitor):
        visitor.visit_triangle(self)

    

@dataclass
class Ellipse(Shape):
    rx: int = 100
    ry: int = 50
    
    def accept(self, visitor):
        visitor.visit_ellipse(self)
    


# Dict of all shapes, used to create Objects form json config
shape_classes = {
    "square": Square,
    "rectangle": Rectangle,
    "circle": Circle,
    "triangle": Triangle,
    "ellipse": Ellipse
}