import pygame

from piece import Piece


POST = 1
CAMPSITE = 2
HEADQUARTER = 3

class Space:
    def __init__(self, id:int, type:int, piece, rect:pygame.Rect, manager, enemy_space:bool = False, connecting_space:bool = False) -> None:
        self.id = id
        self.type = type
        self.piece = piece
        self.rect = rect
        self.piece:Piece|None = piece
        if self.piece:
            self.piece.in_space = self
        if enemy_space:
            manager.add(self, "enemy")
        elif connecting_space:
            manager.add(self, "connecting")
        else:
            manager.add(self)
    
    def check_placable(self, piece:Piece) -> bool:
        if self.piece:
            return False
        
        if self.type == 2:
            return False
        
        value = piece.value
        #Do value checks here
        if value == 12 and self.type != 3:
            return False
        if value >= 10 and self.id <= 10:
            return False
        
        return True
    
    def place(self, piece:Piece):
        self.piece = piece
        
    
    def moved_to(self, piece:Piece) -> bool:
        value = piece.value
        #Do value checks here
        
        return True
    
    def remove_piece(self):
        self.piece = None
    
    def draw(self, screen:pygame.Surface):
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 255, 0, 100), surface.get_rect())
        screen.blit(surface, self.rect)
        
        
    

    