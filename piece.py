import pygame

from spaces import Space
from game import Game
from utils import get_distance

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

class PieceManager:
    def __init__(self, game:Game) -> None:
        self.game = game
        self.pieces:list[Piece] = []
        self.focus:Piece|None = None
        
        self.spaces:list[Space] = []
        
        self._changed = False
        
    
    def add(self, obj:Piece|Space):
        if isinstance(obj, Piece):
            self.pieces.append(obj)
        elif isinstance(obj, Space):
            self.spaces.append(obj)
    
    def handle_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.focus:
                self.on_unfocus()
            for piece in self.pieces:
                if piece.rect.collidepoint(event.pos):
                    piece.on_focus()
                    self.focus = piece
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if not self.focus:
                return
            self.on_unfocus()
        
        elif event.type == pygame.MOUSEMOTION:
            if not self.focus:
                return
            self.focus.move(event.pos)
        
        
    
    
    def on_unfocus(self):
        if self.focus is None:
            return
        self.focus.on_unfocus()
        colliding:list[Space] = []
        
        for space in self.spaces:
            if self.focus.rect.colliderect(space.rect) and space.check_placable(self.focus):
                colliding.append(space)
        
        if not colliding:
            self.focus.rect = self.focus._original_rect
            self.focus = None
            return
        
        min_distance = 10000
        min_distance_index = 0
        for index, space in enumerate(colliding):
            distance = get_distance(space.rect.center, self.focus.rect.center)
            if distance < min_distance:
                min_distance = distance
                min_distance_index = index

        colliding[min_distance_index].place(self.focus)
        self.focus.move(colliding[min_distance_index].rect.topleft)
        self._changed = True
        self.focus = None
        
        
            
            
        
    
    def has_setup_change(self) -> bool:
        if self._changed:
            self._changed = False
            return True
        return False
                
                