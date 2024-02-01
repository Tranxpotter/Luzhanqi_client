import pygame

class Space:
    def __init__(self, id:int, type:int, piece, rect:pygame.Rect) -> None:
        self.id = id
        self.type = type
        self.piece = piece
        self.rect = rect
    
    def 