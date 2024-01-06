from abc import ABC, abstractmethod
from pygame.event import Event as Event

import pygame_gui
import pygame

from network import Network
from game import Game


class Scene(ABC):
    @abstractmethod
    def __init__(self, screen_size:tuple[int, int], network:Network, game:Game) -> None:
        self.network = network
        self.game = game
        self.manager = pygame_gui.UIManager(screen_size)
    @abstractmethod
    async def process_events(self, event:pygame.Event):
        self.manager.process_events(event)

    @abstractmethod
    def update(self, dt:float):
        self.manager.update(dt)

    @abstractmethod
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
    

