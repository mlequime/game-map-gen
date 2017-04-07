# initalize the global variables
import pygame

global TILE_W
global TILE_H

global SCREEN_X
global SCREEN_Y

global STATUSBAR_HEIGHT
global SIDEBAR_WIDTH

global FONT

global COLOR_G
global COLOR_R

# tile dimensions
TILE_W, TILE_H = (24,24)

# screen size in tiles, not pixels (multiply by tile size to get real size)
SCREEN_X, SCREEN_Y = (40, 28)

STATUSBAR_HEIGHT = 20
SIDEBAR_WIDTH = 32

COLOR_G = (50, 240, 120)
COLOR_R = (240, 70, 70)
COLOR_GRAY = (150,150,150)

DEBUG = True