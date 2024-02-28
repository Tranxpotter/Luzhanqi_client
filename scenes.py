from pygame.event import Event as Event

import pygame_gui
import pygame

from network import Network
import game as game_mod
from game import Game
from piece import Piece
from piece_manager import SetupPieceManager, PlayingPieceManager
from space import Space
from utils import *


class Scene:
    def __init__(self, screen_size:tuple[int, int], network:Network, game:Game) -> None:
        self.network = network
        self.game = game
        self.manager = pygame_gui.UIManager(screen_size)
        
    async def process_events(self, event:pygame.Event):
        self.manager.process_events(event)

    def update(self, dt:float):
        self.manager.update(dt)

    def draw_ui(self, screen:pygame.Surface):
        self.manager.draw_ui(screen)



class Login(Scene):
    def __init__(self, screen_size:tuple[int, int], network:Network, game:Game) -> None:
        self.network = network
        self.game = game
        self.manager = pygame_gui.UIManager(screen_size)
        self.manager.get_theme().load_theme("themes/login_theme.json")

        self.username_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect(0, 0, 300, 100), self.manager, 
            anchors={"centerx":"centerx", "centery":"centery"}, 
            placeholder_text="username...", 
            object_id=pygame_gui.core.ObjectID("#username_input", "@username_input"))
        self.username_input.length_limit = 13
        self.start_button = pygame_gui.elements.UIButton(
            pygame.Rect(10, 0, 100, 100),
            "start",
            self.manager,
            object_id=pygame_gui.core.ObjectID("#start_btn", "@start_btn"),
            anchors={"centery":"centery", "left":"left", "left_target":self.username_input}
        )
    
    async def process_events(self, event:pygame.Event):
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.username_input:
                username:str = event.text
                if username:
                    await self.on_login(username)
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                username:str = self.username_input.text
                if username:
                    await self.on_login(username)

        self.manager.process_events(event)
    
    def update(self, dt:float):
        self.manager.update(dt)
    
    def draw_ui(self, screen):
        self.manager.draw_ui(screen)

    async def on_login(self, username):
        data = await self.network.login(username)
        if data:
            self.game.update(data["game"])






class Waiting(Scene):
    def __init__(self, screen_size:tuple[int, int], network:Network, game:Game) -> None:
        self.network = network
        self.game = game
        self.manager = pygame_gui.UIManager(screen_size)
        self.manager.get_theme().load_theme("themes/waiting_theme.json")

        self.waiting_label = pygame_gui.elements.UILabel(
            pygame.Rect(0,-100,700,200),
            "Waiting for players to join",
            self.manager,
            anchors={"center":"center"},
            object_id=pygame_gui.core.ObjectID("#waiting_label", "@waiting_label"))
        
        self.players_label = pygame_gui.elements.UITextBox(
            "\n".join(self.game.players),
            pygame.Rect(0,150,500,300),
            self.manager,
            anchors={"center":"center"},
            object_id=pygame_gui.core.ObjectID("#players_label", "@players_label"))
    
    async def process_events(self, event: Event):
        return await super().process_events(event)
    
    def update(self, dt):
        self.players_label.set_text("\n".join(self.game.players))
        return super().update(dt)
    
    def draw_ui(self, screen):
        return super().draw_ui(screen)
    

class Setup(Scene):
    def __init__(self, screen_size: tuple[int, int], network: Network, game: Game) -> None:
        super().__init__(screen_size, network, game)
        self.manager.get_theme().load_theme("themes/setup_theme.json")
        
        players_display_rect = pygame.Rect(0, 0, 256, 144)
        players_display_rect.topright = (0, 0)
        self.players_display = pygame_gui.elements.UITextBox(
            "<br>".join([player_name + " " + game_mod.STATES[player_state] for player_name, player_state in zip(self.game.players, self.game.player_states)]), 
            players_display_rect,
            manager=self.manager, 
            anchors={"right":"right", "top":"top"},
            object_id=pygame_gui.core.ObjectID("#players_display", "@players_display"))
        
        piece_selection_panel_rect = pygame.Rect(0, 0, 256, 576)
        piece_selection_panel_rect.bottomright = (0, 0)
        self.piece_selection_panel = pygame_gui.elements.UIPanel(
            piece_selection_panel_rect, 
            manager=self.manager, 
            anchors={"right":"right", "bottom":"bottom"},
            object_id=pygame_gui.core.ObjectID("#piece_selection_panel", "@piece_selection_panel"))
        
        self.piece_manager = SetupPieceManager(self.game)
        
        self.pieces:list[Piece] = []
        piece_values = [9, 8, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 10, 10, 11, 11, 11, 12]
        
        piece_size = piece_width, piece_height = (85, 40)
        row_height = 44
        column_width = 128
        
        for index, piece_value in enumerate(piece_values):
            x, y = index%2 * column_width, index//2 * row_height
            
            piece = Piece(pygame.Rect(x + 1030, y + 150, piece_width, piece_height), piece_value, self.piece_manager, piece_size)
            self.pieces.append(piece)
        
        self.spaces:list[Space] = []
        
        ready_btn_rect = pygame.Rect(0, 0, 85, 40)
        ready_btn_rect.bottomright = (0, 0)
        self.ready_btn = pygame_gui.elements.UIButton(ready_btn_rect, 
                                                 "Ready", manager=self.manager, 
                                                 anchors={"right":"right", "bottom":"bottom"},
                                                 object_id=pygame_gui.core.ObjectID("#ready_btn", "@ready_btn"),
                                                 starting_height=2
                                                 )
        self.ready_btn.visible = 0
        
        
        self.ready = False
        
    
        
        
    def space_setup(self):
        x_start = 40
        x_spacing = 209
        y_start = 40
        y_spacing = 120
        
        width, height = 85, 40
        
        for space_info in self.game.board:
            space_id = space_info[0]
            x = (space_id - 1) % 5 * x_spacing + x_start
            y = (space_id - 1) // 5 * y_spacing + y_start
            space = Space(space_id, space_info[1], space_info[2], pygame.Rect(x, y, width, height), self.piece_manager)
            self.spaces.append(space)
        
        
    async def process_events(self, event: Event):
        if self.ready:
            return
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.ready_btn:
            await self.network.ready()
            self.ready = True
            return
        setup_changed = self.piece_manager.handle_event(event)
        if setup_changed:
            await self.network.setup_change([space.id for space in self.spaces], [None if space.piece is None else space.piece.value for space in self.spaces])
        await super().process_events(event)
    
    def update(self, dt: float):
        self.players_display.set_text("<br>".join([player_name + " " + game_mod.STATES[player_state] for player_name, player_state in zip(self.game.players, self.game.player_states)]))
        if all([piece.in_space for piece in self.pieces]):
            self.ready_btn.visible = 1
        else:
            self.ready_btn.visible = 0
        
        super().update(dt)
    
    def draw_ui(self, screen: pygame.Surface):
        board_image = pygame.image.load("assets/player_board.png")
        screen.blit(board_image, (0, 0))
        
        super().draw_ui(screen)
        self.piece_manager.draw(screen)
        


class Playing(Scene):
    def __init__(self, screen_size: tuple[int, int], network: Network, game: Game) -> None:
        super().__init__(screen_size, network, game)
        self.manager.get_theme().load_theme("themes/playing_theme.json")
        
        players_display_rect = pygame.Rect(0, 0, 256, 144)
        players_display_rect.topright = (0, 0)
        self.players_display = pygame_gui.elements.UITextBox(
            "<br>".join([(player_name if index + 1 != self.network.player_num else player_name + " (YOU)") + " <--" if index + 1 == self.game.turn else player_name for index, player_name in enumerate(self.game.players)]),
            players_display_rect,
            manager=self.manager, 
            anchors={"right":"right", "top":"top"},
            object_id=pygame_gui.core.ObjectID("#players_display", "@players_display"))
        
        history_display_rect = pygame.Rect(0, 0, 256, 576)
        history_display_rect.bottomright = (0, 0)
        
        
        self.piece_manager = PlayingPieceManager(self.game, self.network)
        
        self.board_pos = (0, 0)
        self._holding_key = None
        self._move_velocity = 1000
        self.board_zoom = 1
        
        
        self.winning_text = pygame_gui.elements.UILabel(pygame.Rect(0, 0, 600, 200),
                                                        "You WIN!",
                                                        self.manager,
                                                        object_id=pygame_gui.core.ObjectID("#winning_text", "@result"),
                                                        anchors={"center":"center"})
        self.winning_text.visible = 0
        
        self.losing_text = pygame_gui.elements.UILabel(pygame.Rect(0, -100, 600, 200),
                                                        "You LOSE!",
                                                        self.manager,
                                                        object_id=pygame_gui.core.ObjectID("#losing_text", "@result"),
                                                        anchors={"center":"center"})
        self.losing_text.visible = 0
        
        self.return_btn = pygame_gui.elements.UIButton(pygame.Rect(0, 100, 500, 100),
                                                       "Return to main menu",
                                                       self.manager,
                                                       object_id=pygame_gui.core.ObjectID("#return_btn", "@result_btn"),
                                                       anchors={"center":"center"})
        self.return_btn.visible = 0
        
        self._done_end_seq = False
        
        self.history = []
        self.view_history_mode = False
        history_display_rect = pygame.Rect(0, 0, 256, 576)
        history_display_rect.bottomright = (0, 0)
        self.history_display = pygame_gui.elements.UIPanel(history_display_rect,
                                                           1,
                                                           self.manager,
                                                           anchors={"right":"right", "bottom":"bottom"})
        
        self._saved_curr_state = False
        
        self.history_btns = []
        
        
    
        
        
        
    
    def setup(self, board:list[list]):
        if not self._saved_curr_state:
            self.history.append(board)
            btn_height = (len(self.history) - 1) * 50
            btn = pygame_gui.elements.UIButton(pygame.Rect(0, btn_height, 256, 50), 
                                               "2" if self.game.turn == 1 else "1",
                                               self.manager,
                                               self.history_display,
                                               object_id=pygame_gui.core.ObjectID(f"#history_{len(self.history) - 1}", "@history_btn"))
            self.history_btns.append(btn)
            self._saved_curr_state = True
        self.piece_manager.reset()
        player_boards, connecting_spaces = board
        player_num = self.network.player_num
        enemy_num = 2 if player_num == 1 else 1
        self_board = player_boards[player_num-1]
        enemy_board = player_boards[enemy_num-1]
        
        piece_size = piece_width, piece_height = (100, 50)
        row_height = 150
        column_width = 250
        
        start_x, start_y = (50, 50)
        for space in enemy_board[1]:
            space_id, space_type, piece_value = space
            space_x = (30-space_id) % 5 * column_width + start_x
            space_y = (30-space_id) // 5 * row_height + start_y
            if piece_value:
                piece = Piece(pygame.Rect(space_x, space_y, piece_width, piece_height), piece_value, self.piece_manager, piece_size)
            else:
                piece = None
            Space(space_id, space_type, piece, pygame.Rect(space_x, space_y, piece_width, piece_height), self.piece_manager, enemy_space=True)

        start_x, start_y = 50, 1025
        for space in connecting_spaces:
            space_id, space_type, piece_value = space
            space_pos = 3-space_id if player_num == 2 else space_id-1
            space_x = space_pos * column_width * 2 + start_x
            space_y = start_y
            if piece_value:
                piece = Piece(pygame.Rect(space_x, space_y, piece_width, piece_height), piece_value, self.piece_manager, piece_size)
            else:
                piece = None
            Space(space_id, space_type, piece, pygame.Rect(space_x, space_y, piece_width, piece_height), self.piece_manager, connecting_space=True)
        
            
        start_x, start_y = (50, 1250)
        for space in self_board[1]:
            space_id, space_type, piece_value = space
            space_x = (space_id-1) % 5 * column_width + start_x
            space_y = (space_id-1) // 5 * row_height + start_y
            if piece_value:
                piece = Piece(pygame.Rect(space_x, space_y, piece_width, piece_height), piece_value, self.piece_manager, piece_size)
            else:
                piece = None
            Space(space_id, space_type, piece, pygame.Rect(space_x, space_y, piece_width, piece_height), self.piece_manager)
        
    def move_board(self, direction, magnitude):
        board_x = 0 if self.board_pos[0] - direction[0] * magnitude < 0 else int(self.board_pos[0] - direction[0] * magnitude)
        board_y = 0 if self.board_pos[1] - direction[1] * magnitude < 0 else int(self.board_pos[1] - direction[1] * magnitude)
        self.board_pos = (board_x, board_y)
    
    async def process_events(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e or event.key == pygame.K_PAGEDOWN:
                self.board_zoom += 0.1
                if self.board_zoom > 2:
                    self.board_zoom = 2
                    
            elif event.key == pygame.K_q or event.key == pygame.K_PAGEUP:
                self.board_zoom -= 0.1
                if self.board_zoom < 0.5:
                    self.board_zoom = 0.5
                    
            else:
                self._holding_key = event.key
            
        elif event.type == pygame.KEYUP:
            if event.key == self._holding_key:
                self._holding_key = None
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.return_btn:
                self.game.restart = True
            
            elif event.ui_element in self.history_btns:
                history_index = self.history_btns.index(event.ui_element)
                if history_index != len(self.history_btns) - 1:
                    self.view_history_mode = True
                else:
                    self.view_history_mode = False
                self.setup(self.history[history_index])
        
        if not self.view_history_mode:
            await self.piece_manager.handle_event(event, self.board_pos, self.board_zoom)
        await super().process_events(event)


    def update(self, dt: float):
        if not self._done_end_seq and self.game.state == game_mod.END:
            is_win = True if self.game.turn == self.network.player_num else False
            if is_win:
                self.winning_text.visible = 1
            else:
                self.losing_text.visible = 1
            self.return_btn.visible = 1
            
        key_match = {
            pygame.K_w : (0, 1),
            pygame.K_s : (0, -1),
            pygame.K_d : (-1, 0),
            pygame.K_a : (1, 0),
            pygame.K_UP : (0, 1),
            pygame.K_DOWN : (0, -1),
            pygame.K_RIGHT : (-1, 0),
            pygame.K_LEFT : (1, 0)
        }
        if self._holding_key and self._holding_key in key_match.keys():
            self.move_board(key_match[self._holding_key], dt*self._move_velocity)
        
        self.players_display.set_text("<br>".join([(player_name if index + 1 != self.network.player_num else player_name + " (YOU)") + " <--" if index + 1 == self.game.turn else player_name for index, player_name in enumerate(self.game.players)]))

        return super().update(dt)


    def draw_ui(self, screen: pygame.Surface):
        
        board_image = pygame.image.load("assets/Luzhanqi_board.png")
        self.piece_manager.draw(board_image)
        board_image = pygame.transform.scale(board_image, cords_multiply(board_image.get_size(), (self.board_zoom, self.board_zoom)))
        
        screen.blit(board_image, (-self.board_pos[0] * self.board_zoom, -self.board_pos[1] * self.board_zoom))
        
        return super().draw_ui(screen)







