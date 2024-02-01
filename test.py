import pygame

import draggable

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1280, 720)
screen = pygame.display.set_mode(SCREEN_SIZE)

manager = draggable.DraggableManager(screen)

test_piece = draggable.DraggablePiece(manager, 1, pygame.Rect(10, 10, 100, 50))
test_piece_2 = draggable.DraggablePiece(manager, 1, pygame.Rect(20, 10, 100, 50))

clock = pygame.time.Clock()
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        manager.process_event(event)
    
    
    
    screen.fill((255,255,255))
    manager.draw()

    pygame.display.update()

    dt = clock.tick(60) / 1000



pygame.quit()

