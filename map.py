#!/usr/bin/python

import noiselib
from noiselib import fBm, simplex_noise2
from noiselib.modules.main import RescaleNoise
from noiselib.modules.surfaces import PixelArray, RGBLerpNoise

import pygame
import random

import config
import generators


class Tileset:
    def __init__(self, filePath):
        try:
            image = pygame.image.load(filePath).convert_alpha()
            image_w, image_h = image.get_size()

            self.table = []

            for tile_y in range(0, image_h / config.TILE_H):
                for tile_x in range(0, image_w / config.TILE_W):
                    rect = (tile_x * config.TILE_W, tile_y *
                            config.TILE_H, config.TILE_W, config.TILE_H)
                    self.table.append(image.subsurface(rect))

            self.tile_types = {
                'GROUND': 0,
                'GRASS': 1,
                'SAND': 2,
                'SHORE': 3,
                'OCEAN': 4,
                'ICE': 5,
                'SNOW': 6,
                'UI_EMPTY': 7,
                'COLD_GROUND': 8,
                'COLD_GRASS': 9,
                'COLD_SAND': 10,
                'COLD_SHORE': 11,
                'ROAD': 12,
                'CURSOR': 13,

                # items
                'TREES': 17,
                'ROCK': 18,
                'RIVER': 19,

                # road directions
                'ROAD_0': 24,
                'ROAD_1': 25,
                'ROAD_2': 26,
                'ROAD_3': 27,
                'ROAD_4': 28,
                'ROAD_5': 29,
                'ROAD_6': 30,
                'ROAD_7': 31,
                'ROAD_8': 32,
                'ROAD_9': 33,
                'ROAD_10': 34,

                # water directions
                'RIVER_0': 40,
                'RIVER_1': 41,
                'RIVER_2': 42,
                'RIVER_3': 43,
                'RIVER_4': 44,
                'RIVER_5': 45,
                'RIVER_6': 46,
                'RIVER_7': 47,
                'RIVER_8': 48,
                'RIVER_9': 49,
                'RIVER_10': 50,

                # buildings
                'HOUSE': 56,
                'BIGHOUSE': 57,
                'APARTMENTS': 58,
                'STORE': 59,
                'POLICE': 60,
                'FIRE': 61,

                'BULLDOZER': 66

            }


        except Exception, e:
            print "Failed to load tilemap: {}".format(e)
            return None

    def get(self, token):
        if token in self.tile_types:
            return self.table[self.tile_types[token]]
        else:
            return None


class Map:
    def __init__(self, tileset, dim):
        self.set_size(dim)
        self.tileset = tileset
        self.posAt = [0, 0]
        self.destroy = False

        self.layer0 = []
        self.layer1 = []

        self.genIsland()

    def set_size(self, size):
        self.size = size
        self.maxPos = self.size[0] - config.SCREEN_X if self.size[0] > config.SCREEN_X else 0, \
                      self.size[1] - config.SCREEN_Y if self.size[1] > config.SCREEN_Y else 0

    def move(self, dir):
        x, y = self.posAt
        if dir == 'up':
            self.posAt = (x, y - 1) if y > 0 else (x, y)
        elif dir == 'down':
            self.posAt = (x, y + 1) if y < self.size[1] - config.SCREEN_Y - 1 else (x, y)
        elif dir == 'left':
            self.posAt = (x - 1, y) if x > 0 else (x, y)
        elif dir == 'right':
            self.posAt = (x + 1, y) if x < self.size[0] - config.SCREEN_X - 1 else (x, y)

    def genEmpty(self):
        # blank out any existing map
        self.layer0, self.layer1 = [], []
        try:
            for y in range(0, self.size[1]):
                self.layer0.append([])
                self.layer1.append([])
                for x in range(0, self.size[0]):
                    self.layer0[y].append('GRASS')
                    self.layer1[y].append('UI_EMPTY')
        except Exception, e:
            print "Failed at ({},{}) with max dimensions ({},{})".format(x, y, self.size[0], self.size[1])
            return None

    def genRandom(self):
        self.layer0, self.layer1 = [], []
        try:
            for y in range(0, self.size[1]):
                self.layer0.append([])
                self.layer1.append([])
                for x in range(0, self.size[0]):
                    ground_types = ['GRASS', 'GROUND', 'GRASS', 'GRASS']
                    layer_types = ['UI_EMPTY', 'UI_EMPTY', 'UI_EMPTY', 'TREES']
                    number = random.randint(0, 3)
                    number2 = random.randint(0, 3)
                    self.layer0[y].append(ground_types[number])
                    self.layer1[y].append(layer_types[number2])
        except Exception, e:
            print "Failed at ({},{}) with max dimensions ({},{})".format(x, y, self.size[0], self.size[1])
            return None

    def genIsland(self):
        image = generators.MainGenerator().generateIsland(7, "mixed", 1.5).tobytes("raw", "RGB")
        surface = pygame.image.fromstring(image, (2 ** 7 + 1, 2 ** 7 + 1), 'RGB')
        self.genFromImage(surface, (350,350))

    def genFromImage(self, surface, max_size):
        size = surface.get_size()
        dimensions = (0, 0)

        # if it is wider than tall...
        if size[0] >= size[1]:
            # and the width is bigger than the max width, scale it down
            if size[0] > max_size[0]:
                scale = float(max_size[0]) / float(size[0])
                dimensions = (max_size[0], int(round(float(size[1]) * scale)))
            else:
                dimensions = (size[0], size[1])
        # otherwise if the height is bigger than the max height, do the same
        elif size[1] > max_size[1]:
            scale = float(max_size[1]) / float(size[1])
            dimensions = (int(round(float(size[0]) * scale)), max_size[1])

        surface = pygame.transform.smoothscale(surface, dimensions)

        self.set_size(dimensions)

        self.genEmpty()


        for x in range(self.size[0]):
            for y in range(self.size[1]):
                red, green, blue, alpha = surface.get_at((x, y))
                average = (red + green + blue) // 3

                tile = 'GRASS'
                if(average < 50):
                    tile = 'OCEAN'
                elif (average < 70):
                    tile = 'SHORE'
                elif (average < 80):
                    tile = 'SAND'
                elif (average < 200):
                    tile = 'GRASS'
                else:
                    tile = 'GROUND'

                self.layer0[y][x] = tile

    def get(self, loc):
        x, y = loc
        if x < 0 or y < 0 or x > self.size[0] - 1 or y > self.size[1] - 1:
            return None
        else:
            return self.tilemap[x][y]

    def draw(self, screen, offset):
        self.visibleTiles = []

        # if draw coordinates are outside the maximum position, set them back
        # failsafe if the prevention of moving the map does not work
        if self.posAt[0] > self.maxPos[0]:
            self.posAt = (self.maxPos[0], self.posAt[1])

        if self.posAt[1] > self.maxPos[1]:
            self.posAt = (self.posAt[0], self.maxPos[1])

        posX, posY = self.posAt
        active_tile = {}
        for y in range(posY, config.SCREEN_Y + posY):
            if self.size[1] < posY:
                pass
            for x in range(posX, config.SCREEN_X + posX):
                try:
                    if self.size[0] < posX:
                        pass

                    # calculate offset here

                    coords = ((x - posX) * config.TILE_W) + config.SIDEBAR_WIDTH, (y - posY) * config.TILE_H + config.STATUSBAR_HEIGHT

                    tile0 = self.layer0[y][x]
                    tile1 = self.layer1[y][x]

                    active_tile = {
                        'coords': coords,
                        'tile': tile1 if tile1 != 'UI_EMPTY' else tile0,
                        'rect': pygame.Rect(coords[0], coords[1], config.TILE_W, config.TILE_H),
                        'map_xy': (x, y)
                    }
                    self.visibleTiles.append(active_tile)

                    screen.blit(self.tileset.get(tile0), coords)

                    if tile1 == 'UI_EMPTY':
                        pass
                    elif tile1 == 'RIVER' or tile1 == 'ROAD':
                        # wrapping code to connect rivers and roads
                        tile_dir = ""
                        accepted_connections = [tile1]
                        if tile1 == "RIVER":
                            accepted_connections.append("SHORE")
                            accepted_connections.append("OCEAN")
                        if y == 0 or self.layer0[y - 1][x] in accepted_connections or self.layer1[y - 1][x] in accepted_connections:
                            tile_dir += "t"
                        if y == self.size[1] or self.layer0[y + 1][x] in accepted_connections or self.layer1[y + 1][x] in accepted_connections:
                            tile_dir += "b"
                        if x == 0 or self.layer0[y][x - 1] in accepted_connections or self.layer1[y][x - 1] in accepted_connections:
                            tile_dir += "l"
                        if x == self.size[0] or self.layer0[y][x + 1] in accepted_connections or self.layer1[y][x + 1] in accepted_connections:
                            tile_dir += "r"

                        value_table = {
                            't': 1,
                            'l': 0,
                            'b': 1,
                            'r': 0,
                            'lr': 0,
                            'tb': 1,
                            'tl': 2,
                            'tr': 3,
                            'bl': 4,
                            'br': 5,
                            'tbr': 6,
                            'tbl': 7,
                            'tlr': 8,
                            'blr': 9,
                            'tblr': 10
                        }

                        tile1 = "{}_{}".format(tile1, value_table[tile_dir]) if tile_dir in value_table else tile1

                        screen.blit(self.tileset.get(tile1), coords)

                    else:
                        screen.blit(self.tileset.get(tile1), coords)
                except Exception, e:
                    raise Exception(
                        "Tilemap drawing failed at coordinates [{}, {}]. Exception rasied: {}".format(x, y, e))

                if active_tile['rect'].collidepoint(pygame.mouse.get_pos()):
                    possible_cursor = pygame.Surface((20,20))
                    possible_cursor.set_alpha(120)
                    if(self.destroy):
                        if self.layer1[y][x] != 'UI_EMPTY':
                            possible_cursor.fill(config.COLOR_R)
                        else:
                            possible_cursor.set_alpha(0)
                    else:
                        possible_cursor.fill(config.COLOR_G if self.layer1[y][x] == 'UI_EMPTY' else config.COLOR_GRAY)
                    screen.blit(possible_cursor, (active_tile['coords'][0]+2, active_tile['coords'][1]+2))
                    screen.blit(self.tileset.get('CURSOR'), active_tile['coords'])

