import asyncio
import json

import pygame
pygame.init()
import pygame_gui

from network import Network
import game
from game import Game
import scenes


run = True

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
    
    setup_scene = scenes.Setup(SCREEN_SIZE, network, game_info)
    space_setup_done = False
    
    playing_scene = scenes.Playing(SCREEN_SIZE, network, game_info)
    playing_setup_done = False
    
    scene_match:dict[int, scenes.Scene] = {
        game.WAITING : waiting_scene,
        game.SETTING_UP : setup_scene,
        game.READY : setup_scene,
        game.PLAYING : playing_scene,
        game.END : playing_scene
    }
    
    clock = pygame.time.Clock()
    dt = 0
    while game_info.running:
        logged_in = network.player_num != 0
        if logged_in:
            game_info.update(await network.get())
        #Event handling
        if not space_setup_done and game_info.state == game.SETTING_UP:
            space_setup_done = True
            setup_scene.space_setup()
        if game_info.state == game.PLAYING and (not playing_setup_done or game_info.check_turn_changed()):
            playing_setup_done = True
            playing_scene.setup(game_info.board)
        

        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                if network.conn:
                    await network.conn.close()
                game_info.running = False
            if not logged_in:
                await login_scene.process_events(event)
            else:
                await scene_match[game_info.state].process_events(event)
        
        #Update
        if not logged_in:
            login_scene.update(dt)
        else:
            scene_match[game_info.state].update(dt)
        #Drawing
        screen.fill((200, 200, 200))
        if not logged_in:
            login_scene.draw_ui(screen)
        else:
            scene_match[game_info.state].draw_ui(screen)
            

        pygame.display.update()

        

        dt = clock.tick(60) / 1000
    global run
    run = game_info.restart

if __name__ == "__main__":
    while run:
        run = False
        asyncio.run(main())
    pygame.quit()