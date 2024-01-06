import asyncio

import pygame
pygame.init()
import pygame_gui

from network import Network
import scenes




async def main():
    # network = Network()
    # successfully_connected = await network.connect()
    # if not successfully_connected:
    #     print("Server offline")

    SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode(SCREEN_SIZE)

    logged_in = False

    login_scene = scenes.Login(SCREEN_SIZE)
    game_manager = pygame_gui.UIManager(SCREEN_SIZE)
    clock = pygame.time.Clock()
    dt = 0
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
            if not logged_in:
                login_scene.process_events(event)
        
        if not logged_in:
            login_scene.update(dt)
        
        screen.fill((200, 200, 200))
        if not logged_in:
            login_scene.draw_ui(screen)
        
        pygame.display.update()

        

        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    asyncio.run(main())