import pygame

from piece import Piece


POST = 1
CAMPSITE = 2
HEADQUARTER = 3

class Space:
    def __init__(self, id:int, type:int, piece, rect:pygame.Rect, manager) -> None:
        self.id = id
        self.type = type
        self.piece = piece
        self.rect = rect
        self.piece:Piece|None = piece
        manager.add(self)
    
    def check_placable(self, piece:Piece) -> bool:
        if self.piece:
            return False
        
        value = piece.value
        #Do value checks here

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
        pygame.draw.rect(screen, (0, 0, 255), self.rect)
        
        
    

    