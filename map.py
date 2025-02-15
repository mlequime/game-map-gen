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

from ui import Purchasable


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
                'SNOW': 6,

                # resources
                'GROUNDCOAL': 8,
                'GRASSCOAL': 9,
                'SANDCOAL': 10,

                'GROUNDOIL': 6,
                'GRASSOIL': 7,
                'SANDOIL': 14,
                'WATEROIL': 15,

                # items
                'PALMTREE': 11,
                'TREES': 12,
                'MOUNTAIN': 13,

                'ROAD': 31,
                # road directions
                'ROAD_0': 16,
                'ROAD_1': 17,
                'ROAD_2': 18,
                'ROAD_3': 19,
                'ROAD_4': 20,
                'ROAD_5': 21,
                'ROAD_6': 22,
                'ROAD_7': 23,
                'ROAD_8': 24,
                'ROAD_9': 25,
                'ROAD_10': 26,
                'ROAD_11': 27,
                'ROAD_12': 28,
                'ROAD_13': 29,
                'ROAD_14': 30,

                'RIVER': 47,
                # water directions
                'RIVER_0': 32,
                'RIVER_1': 33,
                'RIVER_2': 34,
                'RIVER_3': 35,
                'RIVER_4': 36,
                'RIVER_5': 37,
                'RIVER_6': 38,
                'RIVER_7': 39,
                'RIVER_8': 40,
                'RIVER_9': 41,
                'RIVER_10': 42,
                'RIVER_11': 43,
                'RIVER_12': 44,
                'RIVER_13': 45,
                'RIVER_14': 46,

                # buildings
                'HOUSE': 48,
                'BIGHOUSE': 49,
                'APARTMENTS': 50,
                'STORE': 51,
                'BIGSTORE': 52,
                'POLICE': 53,
                'FIRE': 54,
                'MAYORS': 55,
                'MINE': 56,
                'OILRIG': 57,
                'FERRY': 58,

                # UI
                'UI_EMPTY': 59,
                'CURSOR': 61,
                'UI_LOCKED': 62,
                'BULLDOZER': 63

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
    def __init__(self, tileset, dim, data):

        # Initial setup of variables
        self.size = (0, 0)
        self.max_pos = (0, 0)
        self.visible_tiles = []
        self.tile_at = None

        # The current top-left corner position of the viewfinder, i.e. where to draw the map from
        self.start_pos = (0, 0)
        self.pos_at = [0, 0]

        # map generation variables
        self.rainfall = 2
        self.sea_level = 2

        # Sets the map to the given dimensions
        self.set_size(dim)

        # The tileset used by the map
        self.tileset = tileset

        # A settings which indicates whether the user is destroying an object or
        self.destroy = False

        # The tiles which it is not possible to place objects on
        self.impassable = ['OCEAN', 'SHORE', 'ICE']

        # Modified ores
        self.coal = ['GROUNDCOAL', 'GRASSCOAL', 'SANDCOAL']
        self.oil = ['GROUNDOIL', 'GRASSOIL', 'SANDOIL', 'WATEROIL']

        # The two tile layers for the map instance
        self.layer_0 = []
        self.layer_1 = []

        # A list of all the landmasses, and the playable landmasses
        self.islands = []
        self.playable_islands = []

        # The UI element to be placed
        self.selected_item = None

        # Generate the map based on the input data
        mapgen = generators.GameMapGenerator(self, data)

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

    def add_to_tile(self, loc):
        if self.can_add_to_tile(self.selected_item.ID, loc):
            self.set(loc, 'layer_1', self.selected_item.ID)
            return True
        return False

    def can_add_to_tile(self, tile, loc):
        x, y = loc
        if self.destroy:
            if self.get(loc)['layer_1'] in ['UI_EMPTY', 'RIVER']:
                return False
            return True
        else:
            if self.get(loc)['layer_0'] in self.impassable:
                return False
            if self.get(loc)['layer_1'] != 'UI_EMPTY':
                return False
            if tile == 'ROAD':
                # Roads can only be placed if there is an adjacent road or ferry terminal
                up, down, left, right = False, False, False, False
                if y > 0 and self.get((loc[0], loc[1] - 1))['layer_1'] in ['ROAD','FERRY']:
                    left = True
                if y < self.size[0] - 1 and self.get((loc[0], loc[1] + 1))['layer_1'] in ['ROAD','FERRY']:
                    right = True
                if x > 0 and self.get((loc[0] - 1, loc[1]))['layer_1'] in ['ROAD','FERRY']:
                    left = True
                if x < self.size[0] - 1 and self.get((loc[0] + 1, loc[1]))['layer_1'] in ['ROAD','FERRY']:
                    right = True
                return up or down or left or right
            elif tile in ['HOUSE', 'BIGHOUSE', 'APARTMENTS', 'STORE', 'POLICE', 'FIRE', 'MINE']:
                # Check if the building is near a road (2 tiles).
                # Buildings must be placed near to roads. Oil rigs are exempt.
                near_road = False
                for x in range(loc[0] - 2, loc[0] + 3):
                    for y in range(loc[1] - 2, loc[1] + 3):
                        if self.get((x, y))['layer_1'] == 'ROAD':
                            near_road = True
                return near_road
            elif tile == 'OILRIG':
                near_road = False
                for x in range(loc[0] - 2, loc[0] + 3):
                    for y in range(loc[1] - 2, loc[1] + 3):
                        if self.get((x, y))['layer_1'] == 'ROAD':
                            near_road = True
                return near_road
            return True

    def draw(self, screen, offset):
        """Draws the visible map on the input screen with a given offset."""

        self.visible_tiles = []
        self.tile_at = None

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

                    coords = ((x - posX) * config.TILE_W) + config.SIDEBAR_WIDTH, (
                        y - posY) * config.TILE_H + config.STATUSBAR_HEIGHT

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
                        if tile1 == "ROAD":
                            # Allow roads to connect to the ferry terminals
                            accepted_connections.append("FERRY")
                        if tile1 == "RIVER":
                            # Allow rivers to connect to the shore or oceans
                            accepted_connections.append("SHORE")
                            accepted_connections.append("OCEAN")
                        if y == 0 or self.layer_0[y - 1][x] in accepted_connections or self.layer_1[y - 1][
                            x] in accepted_connections:
                            tile_dir += "t"
                        if y == self.size[1] or self.layer_0[y + 1][x] in accepted_connections or self.layer_1[y + 1][
                            x] in accepted_connections:
                            tile_dir += "b"
                        if x == 0 or self.layer_0[y][x - 1] in accepted_connections or self.layer_1[y][
                                    x - 1] in accepted_connections:
                            tile_dir += "l"
                        if x == self.size[0] or self.layer_0[y][x + 1] in accepted_connections or self.layer_1[y][
                                    x + 1] in accepted_connections:
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

                # Draw the cursor over the currently hovered tile
                if active_tile['rect'].collidepoint(pygame.mouse.get_pos()):
                    possible_cursor = pygame.Surface((20, 20))
                    possible_cursor.set_alpha(120)
                    self.tile_at = {
                        'map_xy': (x, y),
                        'tile': self.get((x, y))
                    }

                    # If no selected item, no cursor
                    if self.selected_item == None:
                        possible_cursor.set_alpha(0)
                    elif (self.destroy):
                        # List of tiles that we cannot destroy
                        if self.tile_at['tile']['layer_1'] not in ['UI_EMPTY', 'RIVER', 'MAYORS']:
                            possible_cursor.fill(config.COLOR_R)
                        else:
                            possible_cursor.set_alpha(0)
                    else:
                        can_place = True
                        if self.selected_item.building != None:
                            can_place = self.selected_item.building.can_place(self.tile_at, self)
                        can_place = can_place and self.can_add_to_tile(self.selected_item.ID, (x, y))
                        possible_cursor.fill(config.COLOR_G if can_place else config.COLOR_GRAY)
                    screen.blit(possible_cursor, (active_tile['coords'][0] + 2, active_tile['coords'][1] + 2))
                    screen.blit(self.tileset.get('CURSOR'), active_tile['coords'])
