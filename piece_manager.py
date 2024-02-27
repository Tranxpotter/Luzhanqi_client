from typing import Literal

import pygame

from space import Space
from game import Game
from network import Network
from piece import Piece
from utils import *

class SetupPieceManager:
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
            mouse_pos = event.pos
            piece_x, piece_y = mouse_pos[0] - self.focus.rect.width // 2, mouse_pos[1] - self.focus.rect.height // 2
            self.focus.move((piece_x, piece_y))
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.auto_place()
        
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
        
        self.place_piece(self.focus, colliding[min_distance_index])
        self.focus = None
        
    
    def has_setup_change(self) -> bool:
        if self._changed:
            self._changed = False
            return True
        return False
    
    def draw(self, screen:pygame.Surface):
        if self.focus:
            for space in self.spaces:
                if space.check_placable(self.focus):
                    space.draw(screen)
        for piece in self.pieces:
            piece.draw(screen)
    
    def auto_place(self):
        for piece in reversed(self.pieces):
            for space in self.spaces:
                if space.check_placable(piece):
                    self.place_piece(piece, space)
                    break
            
            

    def place_piece(self, piece:Piece, space:Space):
        space.place(piece)
        piece.move(space.rect.topleft)
        piece.in_space = space
        self._changed = True
    
    
class PlayingPieceManager:
    def __init__(self, game:Game, network:Network) -> None:
        self.game = game
        self.network = network
        self.enemy_pieces:list[Piece] = []
        self.pieces:list[Piece] = []
        self.focus:Piece|None = None
        
        self.enemy_spaces:list[Space] = []
        self.connecting_spaces:list[Space] = []
        self.spaces:list[Space] = []
        
        self._origin_space = None
        self._changed = False
        
    
    def add(self, obj:Piece|Space, space_type:Literal["enemy", "self", "connecting"] = "self"):
        if isinstance(obj, Piece):
            if obj.value == 13:
                self.enemy_pieces.append(obj)
            else:
                self.pieces.append(obj)
        elif isinstance(obj, Space):
            if space_type == "self":
                self.spaces.append(obj)
            elif space_type == "connecting":
                self.connecting_spaces.append(obj)
            else:
                self.enemy_spaces.append(obj)
    
    def reset(self):
        self.enemy_pieces = []
        self.pieces = []
        self.enemy_spaces = []
        self.connecting_spaces = []
        self.spaces = []
        self.focus = None
        self._changed = False
    
    
    async def handle_event(self, event:pygame.Event, board_pos:tuple[int|float, int|float], board_zoom:float):
        board_zoom_tup = (board_zoom, board_zoom)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] > 1024:
                return
            if self.focus:
                await self.on_unfocus()
            for piece in self.pieces:
                if piece.rect.collidepoint(cords_add(cords_divide(event.pos, board_zoom_tup), board_pos)):
                    self._origin_space = piece.in_space
                    piece.on_focus()
                    self.focus = piece
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if not self.focus:
                return
            await self.on_unfocus()
        
        elif event.type == pygame.MOUSEMOTION:
            if event.pos[0] > 1024:
                return
            if not self.focus:
                return
            mouse_pos = cords_add(cords_divide(event.pos, board_zoom_tup), board_pos)
            piece_x, piece_y = mouse_pos[0] - self.focus.rect.width // 2, mouse_pos[1] - self.focus.rect.height // 2
            self.focus.move((piece_x, piece_y))
        
        if self.has_setup_change():
            return True
        return False
        
    async def on_unfocus(self):
        if self.focus is None:
            return
        self.focus.on_unfocus()
        colliding:list[Space] = []
        
        for space in self.spaces:
            if self.focus.rect.colliderect(space.rect) and (space.piece is None or space.piece.value == 13):
                colliding.append(space)
        
        for space in self.connecting_spaces:
            if self.focus.rect.colliderect(space.rect) and (space.piece is None or space.piece.value == 13):
                colliding.append(space)
        
        for space in self.enemy_spaces:
            if self.focus.rect.colliderect(space.rect) and (space.piece is None or space.piece.value == 13):
                colliding.append(space)
        
        if not colliding:
            self.focus.rect = self.focus._original_rect
            self.focus.in_space = self._origin_space
            self.focus = None
            return
        
        min_distance = 10000
        min_distance_index = 0
        for index, space in enumerate(colliding):
            distance = get_distance(space.rect.center, self.focus.rect.center)
            if distance < min_distance:
                min_distance = distance
                min_distance_index = index

        if self._origin_space is None:
            origin_space_info = (4, 0)
        elif self._origin_space in self.spaces:
            origin_space_info = (self.network.player_num, self._origin_space.id)
        elif self._origin_space in self.enemy_spaces:
            origin_space_info = (2 if self.network.player_num == 1 else 1, self._origin_space.id)
        elif self._origin_space in self.connecting_spaces:
            origin_space_info = (3, self._origin_space.id)
        else:
            origin_space_info = (4, 0)
        
        
        dest_space = colliding[min_distance_index]
        if dest_space in self.spaces:
            dest_space_info = (self.network.player_num, dest_space.id)
        elif dest_space in self.enemy_spaces:
            dest_space_info = (2 if self.network.player_num == 1 else 1, dest_space.id)
        elif dest_space in self.connecting_spaces:
            dest_space_info = (3, dest_space.id)
        else:
            dest_space_info = (4, 0)
        
        self.focus.rect = self.focus._original_rect
        self.focus.in_space = self._origin_space
        await self.network.play(origin_space_info, dest_space_info)
        self._changed = True
        self.focus = None
        self._origin_space = None
    
    def has_setup_change(self) -> bool:
        if self._changed:
            self._changed = False
            return True
        return False
    
    
    def draw(self, screen:pygame.Surface):
        for piece in self.enemy_pieces:
            piece.draw(screen)
        for piece in self.pieces:
            piece.draw(screen)