import asyncio
import json

import pygame
pygame.init()
import pygame_gui

from network import Network
import game
from game import Game
import scenes




async def main():
    network = Network()
    game_info = Game(0, [], [], 0, [])
    successfully_connected = await network.connect()
    if not successfully_connected:
        print("Server offline")

    SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode(SCREEN_SIZE)

    login_scene = scenes.Login(SCREEN_SIZE, network, game_info)
    waiting_scene = scenes.Waiting(SCREEN_SIZE, network, game_info)
    
    clock = pygame.time.Clock()
    dt = 0
    running = True
    while running:
        logged_in = network.player_num != 0
        if logged_in:
            game_info.update(await network.get())
        #Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                if network.conn:
                    await network.conn.close()
                running = False
            if not logged_in:
                await login_scene.process_events(event)
            elif game_info.state == game.WAITING:
                await waiting_scene.process_events(event)
        
        #Update
        if not logged_in:
            login_scene.update(dt)
        elif game_info.state == game.WAITING:
            waiting_scene.update(dt)
        
        #Drawing
        screen.fill((200, 200, 200))
        if not logged_in:
            login_scene.draw_ui(screen)
        elif game_info.state == game.WAITING:
            waiting_scene.draw_ui(screen)

        pygame.display.update()

        

        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    asyncio.run(main())
    pygame.quit()