#!/usr/bin/python

import noiselib
from noiselib import fBm, simplex_noise2
from noiselib.modules.main import RescaleNoise
from noiselib.modules.surfaces import PixelArray, RGBLerpNoise

import sys
import math
import random

import pygame

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

        # map generation variables
        self.rainfall = 2
        self.sea_level = 2

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

        # A list of all the landmasses, and the playable landmasses
        self.islands = []
        self.playable_islands = []

        # Generate an island
        self.gen_island()

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



        # Define the islands
        self.define_islands()
        # Generate rivers
        self.gen_rivers(surface)
        # Generate forests
        self.gen_forests()

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

        # Change the recursion limit to permit the scanning of the map
        sys.setrecursionlimit(20000)
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
        self.islands = sorted(islands, key=len)
        self.islands.reverse()
        self.playable_islands = [x for x in self.islands if len(x) > 50]

        # Return the recursion limit to normal value
        sys.setrecursionlimit(1000)

    def find_island_boundaries(self, visited_tiles, island_tiles, loc):
        """Walks around the map exploring an island to discover its boundaries."""
        x,y = loc
        # Quit if we've already logged this tile
        if loc in visited_tiles:
            return
        visited_tiles.append(loc)

        # Quit if the tile is water or ice
        if self.get(loc)['layer_0'] in self.impassable:
            return

        # Quit if we've already logged this tile in this current island (failsafe)
        if loc in island_tiles:
            return
        island_tiles.append(loc)

        # Spread out recursively and find all the tiles that we can
        if x > 0:
            if self.get((x-1,y))['layer_0'] not in self.impassable and (x-1,y) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x-1,y))
        if x < self.size[0]:
            if self.get((x+1, y))['layer_0'] not in self.impassable and (x+1,y) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x+1,y))

        if y > 0:
            if self.get((x,y-1))['layer_0'] not in self.impassable and (x,y-1) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x,y-1))
        if y < self.size[0]:
            if self.get((x, y+1))['layer_0'] not in self.impassable and (x,y+1) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x,y+1))

    def gen_rivers(self, surface):
        """Generates rivers on the map, using the surface heights as a basis."""
        if len(self.islands) == 0:
            self.define_islands()

        for island in self.islands:
            if len(island) < 40:
                continue

            min_rivers = 1
            if len(island) > ((self.size[0] + self.size[1])/2) ** 1.15:
                min_rivers = 2

            # calculate a maximum number of forests
            rivers_count = min(min_rivers + 3, int(math.sqrt(len(island)) / 2))
            rivers_count = random.randint(min_rivers, rivers_count)

            height_values = [{'value': self.averageRGB(surface.get_at(x)), 'loc': x} for x in island]
            height_values = sorted(height_values,key=lambda x: x['value'])

            while rivers_count > 0:
                start_point = height_values[random.randint(int(len(height_values) * 0.7), int(len(height_values) * 0.95))]['loc']
                river_set = []
                if self.draw_river(surface, start_point, river_set):
                    rivers_count -= 1
                    for loc in river_set:
                        self.set(loc, 'layer_1', 'RIVER')
                else:
                    river_set = []

    def draw_river(self, surface, loc, river_set):

        # Get the location and ensure it's within boundaries
        x,y = loc
        if x < 0 or y < 0 or x > self.size[0] - 1 or y > self.size[1] - 1:
            return False

        if self.get(loc)['layer_1'] == 'RIVER' or loc in river_set:
            return False

        river_set.append(loc)

        current_val = self.averageRGB(surface.get_at(loc))

        possible_dirs = []

        if y > 0 and self.averageRGB(surface.get_at((x,y-1))) <= current_val:
            possible_dirs.append('up')
        if y < self.size[1] - 1 and self.averageRGB(surface.get_at((x,y+1))) <= current_val:
            possible_dirs.append('down')
        if x > 0 and self.averageRGB(surface.get_at((x-1,y))) <= current_val:
            possible_dirs.append('left')
        if x < self.size[0] - 1 and self.averageRGB(surface.get_at((x+1,y))) <= current_val:
            possible_dirs.append('right')


        if len(possible_dirs) == 0:
            return False

        # % chance of river splitting into multiple directions
        if random.randint(1,4) < 4:
            possible_dirs = [possible_dirs[random.randint(0,len(possible_dirs)-1)]]

        for dir in possible_dirs:
            if dir == 'up':
                loc = (x, y-1)
            elif dir == 'down':
                loc = (x, y+1)
            elif dir == 'left':
                loc = (x-1, y)
            elif dir == 'right':
                loc = (x+1, y)

            if self.get(loc)['layer_0'] == 'SHORE' or self.get(loc)['layer_0'] == 'OCEAN':

                # generate some river deltas if possible
                if x > 0 and self.get((x-1,y))['layer_0'] not in self.impassable:
                    river_set.append((x-1, y))
                if x < self.size[0] - 1 and self.get((x+1,y))['layer_0'] not in self.impassable:
                    river_set.append((x+1, y))
                if y > 0 and self.get((x,y-1))['layer_0'] not in self.impassable:
                    river_set.append((x,y-1))
                if y < self.size[1] - 1 and self.get((x,y+1))['layer_0'] not in self.impassable:
                    river_set.append((x,y+1))

                # success!
                return True

            return self.draw_river(surface, loc, river_set)

    def gen_forests(self):
        """Generates forests on the larger islands of the map."""
        if len(self.islands) == 0:
            self.define_islands()

        for island in self.islands:
            if len(island) < 30:
                continue

            min_forests = 0
            # If it's a particularly big island relative to the map size, we should need a few forests
            if len(island) > ((self.size[0] + self.size[1])/2) ** 1.15:
                min_forests = 3

            # calculate a maximum number of forests
            forest_count = max(min_forests + 2, int(math.sqrt(len(island)) / 1.5))

            if forest_count < min_forests:
                forest_count = min_forests
            else:
                forest_count = random.randint(min_forests,forest_count)

            counted_tiles = []
            while forest_count > 0:
                # pick a random start point on the island
                loc = island[random.randint(0,len(island)-1)]

                # keep a list of tiles we've visited
                if loc in counted_tiles:
                    continue
                # forests can only start on grass
                if self.get(loc)['layer_0'] != 'GRASS':
                    counted_tiles.append(loc)
                    continue
                # if counted every tile on the island and there's no grass, exit
                if len(counted_tiles) >= len(island):
                    break

                self.grow_trees(loc, 'up', random.randint(6,12))
                self.grow_trees(loc, 'down', random.randint(6,12))
                self.grow_trees(loc, 'left', random.randint(6,12))
                self.grow_trees(loc, 'right', random.randint(6,12))
                forest_count -= 1



    def grow_trees(self, loc, direction, weight):
        """Part of the forest generation. Grows a branch of a forest in a given direction."""

        # Get the location and ensure it's within boundaries
        x,y = loc
        if x < 0 or y < 0 or x > self.size[0] - 1 or y > self.size[1] - 1:
            return

        # trees should only grow on grass, not sand or other land types
        tile = self.get(loc)
        if tile['layer_0'] != 'GRASS' or tile['layer_1'] not in ['UI_EMPTY', 'TREES']:
            return

        self.set(loc, 'layer_1', 'TREES')

        if weight == 1:
            return

        new_direction = direction
        # prefer for the branches to spread in the same direction, but give it a small chance of making a 90deg turn
        # in either direction
        for i in range(1,random.randint(1,3)):
            if random.randint(1,3) > 2:
                if direction == 'up':
                    new_direction = ['left','right'][random.randint(0,1)]
                elif direction == 'down':
                    new_direction = ['left','right'][random.randint(0,1)]
                elif direction == 'left':
                    new_direction = ['up','down'][random.randint(0,1)]
                elif direction == 'right':
                    new_direction = ['up','down'][random.randint(0,1)]

            # recursively call the grow function
            if new_direction == 'up':
                self.grow_trees((loc[0], loc[1]-1), new_direction, weight-1)
            if new_direction == 'down':
                self.grow_trees((loc[0], loc[1]+1), new_direction, weight-1)
            if new_direction == 'left':
                self.grow_trees((loc[0]-1, loc[1]), new_direction, weight-1)
            if new_direction == 'right':
                self.grow_trees((loc[0]+1, loc[1]), new_direction, weight-1)


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

    def set(self, loc, layer, tile):
        """Sets the tile to the given value at location loc, on the layer specified"""

        # Get the location and ensure it's within boundaries
        x, y = loc
        if x < 0 or y < 0 or x > self.size[0] - 1 or y > self.size[1] - 1 or layer not in ['layer_0', 'layer_1']:
            return
        else:
            if layer == 'layer_0':
                self.layer_0[loc[1]][loc[0]] = tile
            elif layer == 'layer_1':
                self.layer_1[loc[1]][loc[0]] = tile

    def averageRGB(self, color):
        """Averages the RGB values into a grayscale color."""
        return int((color.r + color.g + color.b) / 3)

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

