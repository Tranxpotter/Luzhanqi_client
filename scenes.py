import pygame_gui
import pygame

class Login:
    def __init__(self, screen_size:tuple[int, int]) -> None:
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
    
    def process_events(self, event):
        self.manager.process_events(event)
    
    def update(self, dt:float):
        self.manager.update(dt)
    
    def draw_ui(self, screen):
        self.manager.draw_ui(screen)
