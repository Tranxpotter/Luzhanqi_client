import pygame

FIELD_MARSHAL = 9
GENERAL = 8
MAJOR_GENERAL = 7
BRIGADIER_GENERAL = 6
COLONEL = 5
MAJOR = 4
CAPTAIN = 3
LIEUTENANT = 2
ENGINEER = 1
BOMB = 10
LANDMINE = 11
FLAG = 12
ENEMY = 13

class Piece:
    def __init__(self, rect:pygame.Rect, value:int, manager) -> None:
        self.rect = rect
        self._original_rect = rect
        self.value = value
        self.color = (255,0,0)
        manager.add(self)
    
    def move(self, pos:tuple[int|float, int|float]):
        self.rect = pygame.Rect(pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2, self.rect.width, self.rect.height)\
    
    def draw(self, screen:pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)
    
    def on_focus(self):
        self.color = (255, 255, 0)
    
    def on_unfocus(self):
        self.color = (255, 0, 0)

