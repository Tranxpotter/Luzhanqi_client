import pygame
from abc import ABC, abstractmethod

# FIELD_MARSHAL = 9
# GENERAL = 8
# MAJOR_GENERAL = 7
# BRIGADIER_GENERAL = 6
# COLONEL = 5
# MAJOR = 4
# CAPTAIN = 3
# LIEUTENANT = 2
# ENGINEER = 1
# BOMB = 10
# LANDMINE = 11
# FLAG = 12
# ENEMY = 13


class Draggable(ABC):
    @abstractmethod
    def move(self, pos:tuple[int, int]):...

    @abstractmethod
    def on_unfocus(self):...

    @abstractmethod
    def on_focus(self):...

    @abstractmethod
    def draw(self, screen:pygame.Surface):...



class DraggableManager:
    def __init__(self, screen:pygame.Surface) -> None:
        self.objects:list[Draggable] = []
        self.screen = screen
        self.focus = None
    
    def add(self, obj:Draggable):
        self.objects.append(obj)
    
    def remove(self, obj:Draggable):
        self.objects.remove(obj)

    def process_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for object in self.objects:
                rect:pygame.Rect | None = object.__getattribute__("rect")
                if not rect:
                    continue
                if rect.collidepoint(pygame.mouse.get_pos()):
                    object.on_focus()
                    self.focus = object
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.focus:
                self.focus.on_unfocus()
                self.focus = None
        
        elif event.type == pygame.MOUSEMOTION:
            if not self.focus:
                return
            pos = event.pos
            self.focus.move(pos)
    
    def process_events(self, events:list[pygame.Event]):
        for event in events:
            self.process_event(event)

    
    def draw(self):
        for object in self.objects:
            object.draw(self.screen)
    


