#!/usr/bin/python
import pygame
import pygame.locals
import time
# game imports
import config
import map
import ui


screens = []

def run():
    screen = pygame.display.set_mode(
        (config.TILE_W * config.SCREEN_X + config.SIDEBAR_WIDTH, (config.TILE_H * config.SCREEN_Y) + config.STATUSBAR_HEIGHT))
    pygame.init()
    pygame.key.set_repeat(250, 10)

    config.FONT = pygame.font.Font("src/Bugsmirc05.ttf", 16)

    open_screen(screen, 'game', False)

def open_screen(screen, opt, close):
    if close:
        for item in screens:
            item.close()
            del item

    if(opt == "menu"):
        ms = ui.MenuScreen(screen, open_screen)
        screens.append(ms)
        ms.open()
    elif(opt == "game"):
        gs = ui.GameScreen(screen, open_screen)
        screens.append(gs)
        gs.open()

run()