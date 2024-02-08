from pygame.event import Event as Event

import pygame_gui
import pygame

from network import Network
import game as game_mod
from game import Game
from piece import Piece
from piece_manager import PieceManager
from space import Space


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
        
        self.piece_manager = PieceManager(self.game)
        
        self.pieces:list[Piece] = []
        piece_values = [9, 8, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 10, 10, 11, 11, 11, 12]
        
        piece_width, piece_height = (85, 40)
        row_height = 44
        column_width = 128
        
        for index, piece_value in enumerate(piece_values):
            x, y = index%2 * column_width, index//2 * row_height
            
            piece = Piece(pygame.Rect(x + 1030, y + 150, piece_width, piece_height), piece_value, self.piece_manager)
            self.pieces.append(piece)
        
        self.spaces:list[Space] = []
        
        
        
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
        setup_changed = self.piece_manager.handle_event(event)
        if setup_changed:
            await self.network.setup_change([space.id for space in self.spaces], [None if space.piece is None else space.piece.value for space in self.spaces])
        await super().process_events(event)
    
    def update(self, dt: float):
        self.players_display.set_text("<br>".join([player_name + " " + game_mod.STATES[player_state] for player_name, player_state in zip(self.game.players, self.game.player_states)]))
        super().update(dt)
    
    def draw_ui(self, screen: pygame.Surface):
        board_image = pygame.image.load("assets/player_board.png")
        screen.blit(board_image, (0, 0))
        
        super().draw_ui(screen)
        self.piece_manager.draw(screen)
        



















