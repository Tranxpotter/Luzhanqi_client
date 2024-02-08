import pygame

from space import Space
from game import Game
from piece import Piece
from utils import get_distance

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
        
        if self.has_setup_change():
            return True
        return False
        
        
    
    
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
    
    def draw(self, screen:pygame.Surface):
        for piece in self.pieces:
            piece.draw(screen)
                