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
                'ROAD_11': 35,
                'ROAD_12': 36,
                'ROAD_13': 37,
                'ROAD_14': 38,

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
                'RIVER_11': 51,
                'RIVER_12': 52,
                'RIVER_13': 53,
                'RIVER_14': 54,

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
        # Initial setup of variables
        self.size = (0,0)
        self.max_pos = (0,0)
        self.visible_tiles = []

        # Sets the map to the given dimensions
        self.set_size(dim)

        # The tileset used by the map
        self.tileset = tileset

        # The current top-left corner position of the viewfinder, i.e. where to draw the map from
        self.pos_at = [0, 0]
        # A settings which indicates whether the user is destroying an object or
        self.destroy = False

        # The tiles which it is not possible to place objects on
        self.impassable = ['OCEAN','SHORE','ICE']

        # The two tile layers for the map instance
        self.layer_0 = []
        self.layer_1 = []

        # A list of all the landmasses
        self.islands = []

        # Generate an island
        self.gen_island()

        # Define the islands
        self.define_islands()

    def set_size(self, size):
        self.size = size
        self.max_pos = self.size[0] - config.SCREEN_X if self.size[0] > config.SCREEN_X else 0, \
                      self.size[1] - config.SCREEN_Y if self.size[1] > config.SCREEN_Y else 0

    def move(self, dir):
        """Function to move the map in a given direction 'dir' (up/down/left/right)"""
        x, y = self.pos_at
        if dir == 'up':
            self.pos_at = (x, y - 1) if y > 0 else (x, y)
        elif dir == 'down':
            self.pos_at = (x, y + 1) if y < self.size[1] - config.SCREEN_Y - 1 else (x, y)
        elif dir == 'left':
            self.pos_at = (x - 1, y) if x > 0 else (x, y)
        elif dir == 'right':
            self.pos_at = (x + 1, y) if x < self.size[0] - config.SCREEN_X - 1 else (x, y)

    def gen_empty(self):
        """Generates an empty map (just grass and air)"""
        # blank out any existing map
        self.layer_0, self.layer_1 = [], []
        try:
            for y in range(0, self.size[1]):
                self.layer_0.append([])
                self.layer_1.append([])
                for x in range(0, self.size[0]):
                    self.layer_0[y].append('GRASS')
                    self.layer_1[y].append('UI_EMPTY')
        except Exception, e:
            print "Failed at ({},{}) with max dimensions ({},{})".format(x, y, self.size[0], self.size[1])
            return None

    def gen_random(self):
        """Generates a map with a random selection of tiles."""
        self.layer_0, self.layer_1 = [], []
        try:
            for y in range(0, self.size[1]):
                self.layer_0.append([])
                self.layer_1.append([])
                for x in range(0, self.size[0]):
                    ground_types = ['GRASS', 'GROUND', 'GRASS', 'GRASS']
                    layer_types = ['UI_EMPTY', 'UI_EMPTY', 'UI_EMPTY', 'TREES']
                    number = random.randint(0, 3)
                    number2 = random.randint(0, 3)
                    self.layer_0[y].append(ground_types[number])
                    self.layer_1[y].append(layer_types[number2])
        except Exception, e:
            print "Failed at ({},{}) with max dimensions ({},{})".format(x, y, self.size[0], self.size[1])
            return None

    def gen_island(self):
        """Generates an island map."""
        #image = generators.MainGenerator().generateIsland((320,250), "mixed", 1.5).tobytes("raw", "RGB")
        #surface = pygame.image.fromstring(image, image.get_size(), 'RGB')
        surface = generators.MainGenerator().generateIsland(7)
        self.gen_from_image(surface, surface.get_size())

    def gen_from_image(self, surface, max_size):
        """"Generates a map from an image. All generators will generate an image which will then be passed into
        This function to generate the playable map."""
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

        self.gen_empty()


        for x in range(self.size[0]):
            for y in range(self.size[1]):
                red, green, blue, alpha = surface.get_at((x, y))
                average = (red + green + blue) // 3

                tile = 'GRASS'
                if(average < 70):
                    tile = 'OCEAN'
                elif (average < 90):
                    tile = 'SHORE'
                elif (average < 100):
                    tile = 'SAND'
                elif (average < 200):
                    tile = 'GRASS'
                elif (average < 230):
                    tile = 'GROUND'
                else:
                    tile = 'SNOW'

                self.layer_0[y][x] = tile

    def define_islands(self):
        """Explores a map and builds an array of islands it discovers."""
        islands = []
        visited_tiles = []
        for y in range(0, self.size[1]):
            for x in range(0, self.size[0]):
                if (x,y) in visited_tiles:
                    continue
                if self.get((x,y))['layer_0'] not in self.impassable:
                    island_tiles = []
                    self.find_island_boundaries(visited_tiles, island_tiles, (x,y))
                    islands.append(island_tiles)
        self.islands = islands

    def find_island_boundaries(self, visited_tiles, island_tiles, loc):
        """Walks around the map exploring an island to discover its boundaries."""
        x,y = loc
        # Quit if we've already logged this tile
        if loc in island_tiles or loc in visited_tiles:
            return

        visited_tiles.append(loc)
        island_tiles.append(loc)

        # Spread out recursively and find all the tiles that we can
        if x > 0:
            if self.get((x-1,y))['layer_0'] not in self.impassable:
                self.find_island_boundaries(visited_tiles, island_tiles, (x-1,y))
        if x < self.size[0]:
            if self.get((x+1, y))['layer_0'] not in self.impassable:
                self.find_island_boundaries(visited_tiles, island_tiles, (x+1,y))

        if y > 0:
            if self.get((x,y-1))['layer_0'] not in self.impassable:
                self.find_island_boundaries(visited_tiles, island_tiles, (x,y-1))
        if y < self.size[0]:
            if self.get((x, y+1))['layer_0'] not in self.impassable:
                self.find_island_boundaries(visited_tiles, island_tiles, (x,y+1))

    def generateForest(self, map):
        pass

    def growTrees(self, map, direction):
        pass

    def get(self, loc):
        """Returns the tiles available at the given location loc"""
        x, y = loc
        if x < 0 or y < 0 or x > self.size[0] - 1 or y > self.size[1] - 1:
            return None
        else:
            return {
                'layer_0': self.layer_0[y][x],
                'layer_1': self.layer_1[y][x]
            }

    def draw(self, screen, offset):
        """Draws the visible map on the input screen with a given offset."""

        self.visible_tiles = []

        # if draw coordinates are outside the maximum position, set them back
        # failsafe if the prevention of moving the map does not work
        if self.pos_at[0] > self.max_pos[0]:
            self.pos_at = (self.max_pos[0], self.pos_at[1])

        if self.pos_at[1] > self.max_pos[1]:
            self.pos_at = (self.pos_at[0], self.max_pos[1])

        posX, posY = self.pos_at
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

                    tile0 = self.layer_0[y][x]
                    tile1 = self.layer_1[y][x]

                    active_tile = {
                        'coords': coords,
                        'tile': tile1 if tile1 != 'UI_EMPTY' else tile0,
                        'rect': pygame.Rect(coords[0], coords[1], config.TILE_W, config.TILE_H),
                        'map_xy': (x, y)
                    }
                    self.visible_tiles.append(active_tile)

                    screen.blit(self.tileset.get(tile0), coords)

                    if tile1 == 'UI_EMPTY':
                        pass
                    elif tile1 == 'RIVER' or tile1 == 'ROAD':
                        # wrapping code to connect rivers and roads
                        tile_dir = ""
                        accepted_connections = [tile1]
                        if tile1 == "RIVER":
                            # Allow rivers to connect to the shore or oceans
                            accepted_connections.append("SHORE")
                            accepted_connections.append("OCEAN")
                        if y == 0 or self.layer_0[y - 1][x] in accepted_connections or self.layer_1[y - 1][x] in accepted_connections:
                            tile_dir += "t"
                        if y == self.size[1] or self.layer_0[y + 1][x] in accepted_connections or self.layer_1[y + 1][x] in accepted_connections:
                            tile_dir += "b"
                        if x == 0 or self.layer_0[y][x - 1] in accepted_connections or self.layer_1[y][x - 1] in accepted_connections:
                            tile_dir += "l"
                        if x == self.size[0] or self.layer_0[y][x + 1] in accepted_connections or self.layer_1[y][x + 1] in accepted_connections:
                            tile_dir += "r"

                        value_table = {
                            't': 11,
                            'b': 12,
                            'l': 13,
                            'r': 14,
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
                        if self.layer_1[y][x] != 'UI_EMPTY':
                            possible_cursor.fill(config.COLOR_R)
                        else:
                            possible_cursor.set_alpha(0)
                    else:
                        possible_cursor.fill(config.COLOR_G if self.layer_1[y][x] == 'UI_EMPTY' else config.COLOR_GRAY)
                    screen.blit(possible_cursor, (active_tile['coords'][0]+2, active_tile['coords'][1]+2))
                    screen.blit(self.tileset.get('CURSOR'), active_tile['coords'])

