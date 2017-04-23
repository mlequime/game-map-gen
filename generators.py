#!/usr/bin/python

import sys
import copy
import random
import numpy as np

import noiselib
import pygame
import math

from noiselib import fBm, simplex_noise2
from noiselib.modules.surfaces import PixelArray, RGBLerpNoise
from noiselib.modules.main import RescaleNoise

from PIL import Image

import config

class MainGenerator:
    """Generates raw heightmaps with no additional features to be used by the game map generators."""
    def __init__(self):
        noiselib.init(256)
        pass

    # Generators
    def gen_simple_noise(self, scale):
        res = 2 ** scale if scale < 8 else 2 ** 8
        size = (res, res)
        # Generate the noise using noiselib
        src = fBm(8, 0.45, simplex_noise2)
        src = RescaleNoise((-1, 1), (0, 1), src)
        colors = ((0, 0, 0), (233, 233, 233), 1)
        src = RGBLerpNoise(colors, src)

        surface = pygame.Surface((size[0] * 2, size[1] * 2))
        PixelArray(surface, src)

        surface = pygame.transform.smoothscale(surface, size)

        return surface

    def gen_island(self, scale, rainfall):
        """Generates an island map."""
        # Generate a standard map

        # If the scale is 5 or below generate at a higher size then scale down for better results
        slate = self.gen_simple_noise(scale)

        # apply the mask
        slate = self.increase_contrast(slate, 1.4)
        slate = self.mask_radial(slate)
        self.erosion(slate, 4+rainfall)
        return slate

    def gen_continents(self, scale, rainfall):
        """Generates a map with two large continents."""
        # Generate a standard map
        slate = self.gen_simple_noise(scale)

        # apply the mask
        slate = self.increase_contrast(slate, 1.3, 40)
        slate = self.mask_hyperbolic(slate)
        self.erosion(slate, 3+rainfall)
        return slate


    def gen_highlands(self, scale, rainfall):
        """Generates a highland map with high-up land, higher resources and less water or trees."""
        # Generate a standard map
        slate = self.gen_simple_noise(scale)

        # The third parameter, brightness, is what makes this a highland map with a +100 modifier
        slate = self.increase_contrast(slate, 1.3, 100)
        # erode the highland slightly more than the other map types
        self.erosion(slate, 6+rainfall)
        return slate

    # Overlay masks
    def mask_radial(self, surface):
        """Generates a radial mask over an input surface."""
        size = surface.get_size()
        output = pygame.Surface(size)

        for y in range(0, size[1]):
            for x in range(0, size[0]):
                loc = (x - size[0] * 0.5, y - size[1] * 0.5)
                d = float(math.sqrt(loc[0] ** 2 + loc[1] ** 2))

                m = float(size[0]) * 0.5
                change = max(0.0, 1.0 - (d / m)) * 2.5

                # only want to *darken* colors when applying this mask,
                # otherwise appears totally washed out
                old_color = surface.get_at((x, y)).r

                color = int(round(float(old_color * change)))
                if color > old_color:
                    color = old_color
                output.set_at((x, y), pygame.Color(color, color, color, 255))
        return output
    def mask_hyperbolic(self, surface):
        """Generates a hyperbolic paraboloid mask over an input surface."""
        size = surface.get_size()
        output = pygame.Surface(size)
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                useX = (float(x) / (float(size[0]) / 2)) - 1.0
                useY = (float(y) / (float(size[1]) / 2)) - 1.0

                z = (useX ** 2 - useY ** 2) * 2 + 0.5
                old_color = surface.get_at((x, y)).r
                color = int(round(float(max(0.0, old_color * z))))

                if color > old_color:
                    color = old_color
                output.set_at((x, y), pygame.Color(color, color, color, 255))

        return output
    def mask_linear(self, surface):
        """Generates a linear mask over an input surface."""
        size = surface.get_size()
        output = pygame.Surface(size)
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                useX = float(x) / float(size[0] / 2) - 1.0
                useY = float(y) / float(size[0] / 2) - 1.0

                z = ((-useY) ** 2) * 3
                old_color = surface.get_at((x, y)).r
                color = int(round(float(max(0.0, old_color * z))))

                if color > old_color:
                    color = old_color
                output.set_at((x, y), pygame.Color(color, color, color, 255))

        return output

    # Utility functions
    def merge_images(self, mode, *args):
        """Merge two images together, with the output image pixel values being the average of both of the input
        images. Images must be the same size."""
        size = args[0].get_size()
        slate = pygame.Surface(size)

        for surface in args:
            if surface.get_size() != size:
                print "Sizes do not match!"

        for y in range(0, size[1]):
            for x in range(0, size[0]):
                average = []
                for surface in args:
                    color = surface.get_at((x, y))
                    average.append((color.r + color.g + color.b) // 3)
                if mode == "average":
                    av = int(round(sum(average) / len(average)))
                elif mode == "multiply":
                    av = int(min(average))
                try:
                    slate.set_at((x, y), pygame.Color(av, av, av, 255))
                except Exception, e:
                    print av
        return slate
    def brighten_image(self, surface, factor):
        """Brightens an image by multiplying by an input factor."""
        size = surface.get_size()

        for y in range(0, size[1]):
            for x in range(0, size[0]):
                color = surface.get_at((x, y))
                new_color = pygame.Color(color.r * factor, color.g * factor, color.b * factor, 255)
                surface.set_at((x, y), new_color)
        return surface

    def increase_contrast(self, surface, factor, brightness=0):
        """Increases the contract of an input surface by given factor, with option for a brightness modifier"""
        size = surface.get_size()

        for y in range(0, size[1]):
            for x in range(0, size[0]):
                old_color = surface.get_at((x, y)).r
                new_color = int((factor * (old_color - 128)) + 128 + brightness)
                if new_color < 0:
                    new_color = 0
                elif new_color > 255:
                    new_color = 255
                try:
                    surface.set_at((x, y), pygame.Color(new_color, new_color, new_color, 255))
                except Exception, e:
                    print new_color
        return surface

    def averageRGB(self, color):
        """Averages the RGB values into a grayscale color."""
        return int((color.r + color.g + color.b) / 3)

    # Erosion algorithms
    def erosion(self, surface, factor=3):
        """'Erodes' an input surface through the use of a simulated rainfall function. Power or strength of the erosion
        can be controlled with the input factor."""

        times_to_run = 10000 * factor
        size = surface.get_size()

        while times_to_run > 0:
            xy = random.randint(0, size[0] - 1), random.randint(0, size[1] - 1)
            self.erode(surface, size, xy)
            times_to_run -= 1

        pygame.image.save(surface, "erosion_test2.png")
    def erode(self, surface, size, xy):
        """Helper function for erosion. A recursive virtual raindrop that will run down the edges of a mountain on
        the map and erode the terrain as it passes, creating smooth grooves in the landscape. Takes the surface, the
        the size of the surface and the current co-ordinates"""
        x, y = xy
        av = self.averageRGB(surface.get_at(xy))

        av = int(av - random.randint(1, 2))

        if av < 20:
            return

        if av > 255:
            av = 255

        dirs = {
            'top': 0,
            'bottom': 0,
            'left': 0,
            'right': 0
        }

        # if at the extremes of the generated map, assume the pixel value is slightly higher to prevent runoff without
        # skewing averages
        dirs['top'] = av + 1 if y == 0 else self.averageRGB(surface.get_at((x, y - 1)))
        dirs['bottom'] = av + 1 if y == size[1] - 1 else  self.averageRGB(surface.get_at((x, y + 1)))
        dirs['left'] = av + 1 if x == 0 else self.averageRGB(surface.get_at((x - 1, y)))
        dirs['right'] = av + 1 if x == size[0] - 1 else self.averageRGB(surface.get_at((x + 1, y)))

        mean_of_dirs = int((dirs['top'] + dirs['bottom'] + dirs['left'] + dirs['right']) / 4)

        # this prevents the raindrops from 'drilling' holes into the map, if the average of the directions around it are
        # signficantly greater than the spot, don't continue
        if mean_of_dirs - 2 > av:
            return

        surface.set_at(xy, pygame.Color(av, av, av, 255))

        possible_dirs = []
        for dir, value in dirs.iteritems():
            if value < av or (value == av and random.randint(0, 1) == 1):
                possible_dirs.append(dir)

        # if there's flat land pick a random direction

        if len(possible_dirs) == 0:
            return

        if random.randint(0, 1) == 1:
            selections = [possible_dirs[random.randint(0, len(possible_dirs) - 1)]]
        else:
            selections = possible_dirs

        for selection in selections:
            if selection == 'top':
                if y > 0:
                    self.erode(surface, size, (x, y - 1))
            if selection == 'bottom':
                if y < size[1] - 1:
                    self.erode(surface, size, (x, y + 1))
            if selection == 'left':
                if x > 0:
                    self.erode(surface, size, (x - 1, y))
            if selection == 'right':
                if x < size[0] - 1:
                    self.erode(surface, size, (x + 1, y))

    def set_sea_level(self, surface, threshold_value):
        size = surface.get_size()
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                val = self.averageRGB(surface.get_at((x, y)))
                if val < threshold_value:
                    surface.set_at((x, y), pygame.Color(val, val, val, 255))


class GameMapGenerator:
    """A generator for a playable game map. Calls the MainGenerator functions and produces a map with forests,
    rivers or other required feature to enable the player to play on the map."""
    def __init__(self, map, data):
        self.map = map

        self.map_type = data['map']
        self.rainfall = data['rainfall']
        self.resources = data['resources']

        self.scale = 5 + (2 * data['size'])

        if self.map_type == "island":
            self.gen_island()
        elif self.map_type == "highlands":
            self.resources += 5
            self.rainfall -= 1 if self.rainfall > 0 else 0
            self.gen_highlands()
        elif self.map_type == "continents":
            self.rainfall += 1
            self.gen_continents()
        elif self.map_type == "deserts":
            self.rainfall -= 1
            self.gen_island()

    # Map generators
    def gen_empty(self):
        """Generates an empty map (just grass and air)"""
        # blank out any existing map
        self.map.layer_0, self.map.layer_1 = [], []
        try:
            for y in range(0, self.map.size[1]):
                self.map.layer_0.append([])
                self.map.layer_1.append([])
                for x in range(0, self.map.size[0]):
                    self.map.layer_0[y].append('GRASS')
                    self.map.layer_1[y].append('UI_EMPTY')
        except Exception, e:
            print "Failed at ({},{}) with max dimensions ({},{})".format(x, y, self.map.size[0], self.map.size[1])
            return None

    def gen_random(self):
        """Generates a map with a random selection of tiles."""
        self.map.layer_0, self.map.layer_1 = [], []
        try:
            for y in range(0, self.map.size[1]):
                self.map.layer_0.append([])
                self.map.layer_1.append([])
                for x in range(0, self.map.size[0]):
                    ground_types = ['GRASS', 'GROUND', 'GRASS', 'GRASS']
                    layer_types = ['UI_EMPTY', 'UI_EMPTY', 'UI_EMPTY', 'TREE S']
                    number = random.randint(0, 3)
                    number2 = random.randint(0, 3)
                    self.map.layer_0[y].append(ground_types[number])
                    self.map.layer_1[y].append(layer_types[number2])
        except Exception, e:
            print "Failed at ({},{}) with max dimensions ({},{})".format(x, y, self.map.size[0], self.map.size[1])
            return None

    def gen_island(self):
        """Generates an island map."""
        while True:
            print "Generating Island"
            surface = MainGenerator().gen_island(self.scale, self.rainfall)
            self.gen_from_image(surface, surface.get_size())

            if self.gen_playable_elements(surface):
                return

    def gen_continents(self):
        while True:
            print "Generating Continent"
            surface = MainGenerator().gen_continents(self.scale, self.rainfall)
            self.gen_from_image(surface, surface.get_size())

            if self.gen_playable_elements(surface):
                return


    def gen_highlands(self):
        while True:
            print "Generating Highlands"
            surface = MainGenerator().gen_highlands(self.scale, self.rainfall)
            self.gen_from_image(surface, surface.get_size())

            if self.gen_playable_elements(surface):
                return

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

        self.map.set_size(dimensions)

        self.gen_empty()

        for x in range(self.map.size[0]):
            for y in range(self.map.size[1]):
                red, green, blue, alpha = surface.get_at((x, y))
                average = (red + green + blue) / 3

                tile = 'GRASS'
                if average < 50:
                    tile = 'OCEAN'
                elif average < 100:
                    tile = 'SHORE'
                # if desert type, all higher tiles should be sand
                elif self.map_type == "deserts":
                    tile = 'SAND'
                elif average < 200:
                    tile = 'GRASS'
                elif average < 230:
                    tile = 'GROUND'
                else:
                    tile = 'SNOW'

                self.map.layer_0[y][x] = tile

                # 2.5% chance of high elevation tiles generating a mountain
                if tile in ['GROUND', 'SNOW'] and random.randint(0,40) == 0:
                    self.map.layer_1[y][x] = 'MOUNTAIN'

                # 2% chance of desert tiles generating a palm tree
                if tile in ['SAND'] and random.randint(0,50) == 0:
                    self.map.layer_1[y][x] = 'PALMTREE'


    def gen_playable_elements(self, surface):
        # Define the islands
        if self.map_type not in ['deserts','highlands']:
            self.gen_beaches()

        self.gen_snow()

        if self.map_type == 'highlands':
            self.define_landmass()
        else:
            self.define_islands()
        # Generate rivers
        self.gen_rivers(surface)
        # Generate forests
        if self.map_type != 'deserts':
            self.gen_forests()
        # Generate ore veins
        self.gen_ore_veins()
        # Select player startpoint on the largest island
        islands_to_test = sorted(self.map.playable_islands, key=len)
        islands_to_test.reverse()

        for island in islands_to_test:
            if self.select_player_startpoint(island):
                return True
        return False

    # Search and define islands
    def define_islands(self):
        """Explores a map and builds an array of islands it discovers."""
        # Change the recursion limit to permit the scanning of the map
        sys.setrecursionlimit(20000)

        # A list of all the islands (continuous landmasses) and the tiles that we've already visted
        islands = []
        visited_tiles = []

        for y in range(0, self.map.size[1]):
            for x in range(0, self.map.size[0]):
                # If we've already logged this tile, skip it
                if (x, y) in visited_tiles:
                    continue

                if self.map.get((x, y))['layer_0'] not in self.map.impassable:
                    island_tiles = []
                    self.find_island_boundaries(visited_tiles, island_tiles, (x, y))
                    # sort tiles by axes
                    island_tiles = sorted(island_tiles, key=lambda x: (x[1], -x[0]))
                    islands.append(island_tiles)
        self.map.islands = sorted(islands, key=len)
        self.map.islands.reverse()

        # Player doesn't necessarily have to start on the biggest island, but prevent them starting on an island too
        # small to be properly playable
        self.map.playable_islands = [x for x in self.map.islands if len(x) > 400]

        # Return the recursion limit to normal value
        sys.setrecursionlimit(1000)

        # Search and define islands

    def define_landmass(self):
        """Defines the map as a single landmass. For use only with the highlands map type."""
        island = []

        for y in range(0, self.map.size[1]):
            for x in range(0, self.map.size[0]):
                if self.map.get((x,y))['layer_0'] not in self.map.impassable:
                    island.append((x,y))

        self.map.islands = [island]
        self.map.playable_islands = [island]

    def find_island_boundaries(self, visited_tiles, island_tiles, loc):
        """Walks around the map exploring an island to discover its boundaries."""
        x, y = loc
        # Quit if we've already logged this tile
        if loc in visited_tiles:
            return
        visited_tiles.append(loc)

        # Quit if the tile is water or ice
        if self.map.get(loc)['layer_0'] in self.map.impassable:
            return

        # Quit if we've already logged this tile in this current island (failsafe)
        if loc in island_tiles:
            return
        island_tiles.append(loc)

        # Spread out recursively and find all the tiles that we can
        if x > 0:
            if self.map.get((x - 1, y))['layer_0'] not in self.map.impassable and (x - 1, y) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x - 1, y))
        if x < self.map.size[0] - 1:
            if self.map.get((x + 1, y))['layer_0'] not in self.map.impassable and (x + 1, y) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x + 1, y))

        if y > 0:
            if self.map.get((x, y - 1))['layer_0'] not in self.map.impassable and (x, y - 1) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x, y - 1))
        if y < self.map.size[0] - 1:
            if self.map.get((x, y + 1))['layer_0'] not in self.map.impassable and (x, y + 1) not in visited_tiles:
                self.find_island_boundaries(visited_tiles, island_tiles, (x, y + 1))

    def find_island_min_max(self, island):
        """Function to find the upper left corner and lower right corner of an islands occupied rectangle.
        NOTE: This may overlap other islands!"""
        min_x, max_x = (0, 0)
        min_y, max_y = (0, 0)

        for tile in island:
            if tile[0] < min_x:
                min_x = tile[0]
            if tile[0] > max_x:
                max_x = tile[0]
            if tile[1] < min_y:
                min_y = tile[1]
            if tile[1] > max_y:
                max_y = tile[1]

        return ((min_x, max_x),(min_y,max_y))

    def find_island_midpoint(self, island):
        min_x, max_x, min_y, max_y = self.find_island_midpoint(island)

        return ((min_x + max_x)/2, (min_y + max_y)/2)

    # River generation
    def gen_rivers(self, surface):
        """Generates rivers on the map, using the surface heights as a basis."""
        if len(self.map.islands) == 0:
            self.define_islands()

        for island in self.map.islands:
            if len(island) < 40:
                continue

            i_min = max(1, int(len(island) ** (1. / 5)))

            # calculate a maximum number of rivers
            i_max = max(i_min + 3, int(len(island) ** (1. / 3)))

            rivers_count = random.randint(i_min, i_max) + (self.rainfall - 1)

            height_values = [{'value': self.averageRGB(surface.get_at(x)), 'loc': x} for x in island]
            height_values = sorted(height_values, key=lambda x: x['value'])

            while rivers_count > 0:
                start_point = \
                height_values[random.randint(int(len(height_values) * 0.85), int(len(height_values) * 0.98))]['loc']

                river_set = []
                if self.draw_river(surface, start_point, river_set):
                    rivers_count -= 1

                    # perform meandering
                    river_set = self.meander_river(river_set)

                    for loc in river_set:
                        self.map.set(loc, 'layer_1', 'RIVER')
                else:
                    river_set = []

    def meander_river(self, river_set):
        """Takes a river set and adds a manual meander for aesthetic purposes"""
        if len(river_set) > 1:
            last_dir = ''
            count = 0
            straight = 0
            for loc in river_set:
                dir = ''
                if count > 0:
                    if loc[1] < river_set[count - 1][1]:
                        dir = 'up'
                    if loc[1] > river_set[count - 1][1]:
                        dir = 'down'
                    if loc[0] < river_set[count - 1][0]:
                        dir = 'left'
                    if loc[0] > river_set[count - 1][0]:
                        dir = 'right'

                    if last_dir != '' and dir == last_dir:
                        straight += 1
                        # When we hit 4 straight tiles in a row, meander it to improve appearance
                        if straight == 4:
                            old_locs = river_set[count - 4:count]
                            new_locs = []
                            if dir == 'up' or dir == 'down':
                                # perturbing the river flow with a manual set of alterations
                                new_locs = [(old_locs[0][0] - 1, old_locs[0][1] - 1),
                                            (old_locs[0][0] - 1, old_locs[0][1]), (old_locs[1][0] - 1, old_locs[1][1]),
                                            old_locs[1], (old_locs[1][0] + 1, old_locs[1][1]),
                                            (old_locs[2][0] + 1, old_locs[2][1]), (old_locs[3][0] + 1, old_locs[3][1]),
                                            old_locs[3]]

                            if dir == 'left' or dir == 'right':
                                new_locs = [(old_locs[0][0] - 1, old_locs[0][1] - 1),
                                            (old_locs[0][0], old_locs[0][1] - 1), (old_locs[1][0], old_locs[1][1] - 1),
                                            old_locs[1], (old_locs[1][0], old_locs[1][1] + 1),
                                            (old_locs[2][0], old_locs[2][1] + 1), (old_locs[3][0], old_locs[3][1] + 1),
                                            old_locs[3]]
                            # remove the values pre-perturb and add the new ones
                            river_set = [loc for loc in river_set if loc not in old_locs]
                            river_set.extend(new_locs)
                            return river_set
                    else:
                        straight = 0
                        last_dir = dir

                count += 1
            return river_set

    def draw_river(self, surface, loc, river_set, weight=1):

        # Get the location and ensure it's within boundaries
        x, y = loc
        if x < 0 or y < 0 or x > self.map.size[0] - 1 or y > self.map.size[1] - 1:
            return False

        if self.map.get(loc)['layer_1'] == 'RIVER' or loc in river_set:
            return False

        river_set.append(loc)

        current_val = self.averageRGB(surface.get_at(loc))

        possible_dirs = []

        up = 127.5 if y == 0 else self.averageRGB(surface.get_at((x, y - 1)))
        down = 127.5 if y == self.map.size[1] - 1 else self.averageRGB(surface.get_at((x, y + 1)))
        left = 127.5 if x == 0 else self.averageRGB(surface.get_at((x - 1, y)))
        right = 127.5 if x == self.map.size[0] - 1 else self.averageRGB(surface.get_at((x + 1, y)))

        if y > 0 and up <= current_val:
            possible_dirs.append({'dir': 'up', 'value': up})
        if y < self.map.size[1] - 1 and down <= current_val:
            possible_dirs.append({'dir': 'down', 'value': down})
        if x > 0 and left <= current_val:
            possible_dirs.append({'dir': 'left', 'value': left})
        if x < self.map.size[0] - 1 and right <= current_val:
            possible_dirs.append({'dir': 'right', 'value': right})

        if len(possible_dirs) == 0:
            return False

        possible_dirs = sorted(possible_dirs, key=lambda x: x['value'])

        # 25% chance of river splitting into multiple directions
        if random.randint(1, 4) < 4:
            # prefer the second lowest value to encourage meandering
            if len(possible_dirs) > 1:
                dir = possible_dirs[-2]['dir']
            else:
                dir = possible_dirs[0]['dir']

        for dir in possible_dirs:
            if dir['dir'] == 'up':
                loc = (x, y - 1)
            elif dir['dir'] == 'down':
                loc = (x, y + 1)
            elif dir['dir'] == 'left':
                loc = (x - 1, y)
            elif dir['dir'] == 'right':
                loc = (x + 1, y)

            if self.map.get(loc)['layer_0'] == 'SHORE' or self.map.get(loc)['layer_0'] == 'OCEAN':
                if weight > 0:
                    # generate some river deltas if possible
                    if x > 0 and self.map.get((x - 1, y))['layer_0'] not in self.map.impassable:
                        self.draw_river(surface, (x - 1, y), river_set, weight-1)
                    if x < self.map.size[0] - 1 and self.map.get((x + 1, y))['layer_0'] not in self.map.impassable:
                        self.draw_river(surface, (x + 1, y), river_set, weight-1)
                    if y > 0 and self.map.get((x, y - 1))['layer_0'] not in self.map.impassable:
                        self.draw_river(surface, (x, y - 1), river_set, weight-1)
                    if y < self.map.size[1] - 1 and self.map.get((x, y + 1))['layer_0'] not in self.map.impassable:
                        self.draw_river(surface, (x, y + 1), river_set, weight-1)

                # success!
                return True
            elif self.map_type == 'highlands' and len(river_set) > random.randint(10,26):
                return True
            return self.draw_river(surface, loc, river_set)

    # Forest generation
    def gen_forests(self):
        """Generates forests on the larger islands of the map."""
        if len(self.map.islands) == 0:
            self.define_islands()

        for island in self.map.islands:
            if len(island) < 30:
                continue

            i_min = max(1, int(len(island)**(1./4.)))

            # calculate a maximum number of forests
            i_max = max(i_min + 2, int(len(island)**(1./3.) * 1.5))

            # Calculate the number of times to iterate, modified by the rainfall parameter
            forest_count = random.randint(i_min, i_max) + (self.rainfall - 1)*3

            counted_tiles = []
            while forest_count > 0:
                # pick a random start point on the island
                loc = island[random.randint(0, len(island) - 1)]

                # keep a list of tiles we've visited
                if loc in counted_tiles:
                    continue
                # forests can only start on grass
                if self.map.get(loc)['layer_0'] != 'GRASS':
                    counted_tiles.append(loc)
                    continue
                # if counted every tile on the island and there's no grass, exit
                if len(counted_tiles) >= len(island):
                    break

                self.grow_trees(loc, 'up', random.randint(8, 12) + self.rainfall)
                self.grow_trees(loc, 'down', random.randint(8, 12) + self.rainfall)
                self.grow_trees(loc, 'left', random.randint(8, 12) + self.rainfall)
                self.grow_trees(loc, 'right', random.randint(8, 12) + self.rainfall)
                forest_count -= 1

    def grow_trees(self, loc, direction, weight):
        """Part of the forest generation. Grows a branch of a forest in a given direction."""

        # Get the location and ensure it's within boundaries
        x, y = loc
        if x < 0 or y < 0 or x > self.map.size[0] - 1 or y > self.map.size[1] - 1:
            return

        # trees should only grow on grass, not sand or other land types
        tile = self.map.get(loc)
        if tile['layer_0'] != 'GRASS' or tile['layer_1'] not in ['UI_EMPTY', 'TREES']:
            return

        self.map.set(loc, 'layer_1', 'TREES')

        if weight == 1:
            return

        new_direction = direction
        # prefer for the branches to spread in the same direction, but give it a small chance of making a 90deg turn
        # in either direction
        for i in range(1, random.randint(1, 3)):
            if random.randint(1, 3) > 2:
                if direction == 'up':
                    new_direction = ['left', 'right'][random.randint(0, 1)]
                elif direction == 'down':
                    new_direction = ['left', 'right'][random.randint(0, 1)]
                elif direction == 'left':
                    new_direction = ['up', 'down'][random.randint(0, 1)]
                elif direction == 'right':
                    new_direction = ['up', 'down'][random.randint(0, 1)]

            # recursively call the grow function
            if new_direction == 'up':
                self.grow_trees((loc[0], loc[1] - 1), new_direction, weight - 1)
            if new_direction == 'down':
                self.grow_trees((loc[0], loc[1] + 1), new_direction, weight - 1)
            if new_direction == 'left':
                self.grow_trees((loc[0] - 1, loc[1]), new_direction, weight - 1)
            if new_direction == 'right':
                self.grow_trees((loc[0] + 1, loc[1]), new_direction, weight - 1)

    # Ores generation
    def gen_ore_veins(self):
        if len(self.map.islands) == 0:
            self.define_islands()

        for island in self.map.islands:
            if len(island) < 30:
                continue

            i_min, i_max = 1, min(4, int(math.sqrt(len(island)) /3))

            # Modify by the resource abundancy option
            i_max += (self.resources - 1)

            for i in range(i_min, i_max):
                coords = island[random.randint(0, len(island)-1)]

                # 2/3 chance for coal, 1/3 for oil
                if random.randint(0,2) > 0:
                    self.gen_coal_veins(coords,random.randint(4,8))
                else:
                    self.gen_oil_field(coords,random.randint(2,3))

    def gen_coal_veins(self, loc, weight=4):
        if weight < 0:
            return

        tile = self.map.get(loc)
        if tile == None:
            return
        tile_0 = tile['layer_0']

        if tile_0== 'GRASS':
            self.map.set(loc, 'layer_0', 'GRASSCOAL')
        elif tile_0 == 'SAND':
            self.map.set(loc, 'layer_0', 'SANDCOAL')
        elif tile_0 == 'GROUND':
            self.map.set(loc, 'layer_0', 'GROUNDCOAL')
        elif tile_0 in self.map.coal:
            pass
        else:
            return

        # coal veins should draw in a roughly diagonal line
        self.gen_coal_veins((loc[0]-(random.randint(0,1)),loc[1]-(random.randint(0,1))), weight-1)
        self.gen_coal_veins((loc[0]+(random.randint(0,1)),loc[1]+(random.randint(0,1))), weight-1)

    def gen_oil_field(self, loc, weight=3):
        if weight < 0:
            return

        tile = self.map.get(loc)
        if tile == None:
            return

        tile_0 = tile['layer_0']

        if tile_0== 'GRASS':
            self.map.set(loc, 'layer_0', 'GRASSOIL')
        elif tile_0 == 'SAND':
            self.map.set(loc, 'layer_0', 'SANDOIL')
        elif tile_0 == 'GROUND':
            self.map.set(loc, 'layer_0', 'GROUNDOIL')
        elif tile_0 == 'SHORE':
            self.map.set(loc,'layer_0', 'WATEROIL')
        elif tile_0 in self.map.oil:
            pass
        else:
            return

        if random.randint(0,1) == 1:
            self.gen_oil_field((loc[0] - 2, loc[1] - 2), weight-1)
        if random.randint(0,1) == 1:
            self.gen_oil_field((loc[0] - 2, loc[1] + 2), weight-1)
        if random.randint(0,1) == 1:
            self.gen_oil_field((loc[0] + 2, loc[1] - 2), weight-1)
        if random.randint(0,1) == 1:
            self.gen_oil_field((loc[0] + 2, loc[1] + 2), weight-1)

    def gen_beaches(self):
        new_map = copy.deepcopy(self.map)

        for x in range(0, self.map.size[0]):
            for y in range(0, self.map.size[1]):
                tiles, count = (0,0)

                for nx in range(x-1, x+2):
                    for ny in range(y-1, y+2):
                        tile_at = self.map.get((nx,ny))
                        # If the tile is off the map, or it is not water and it is the current tile, do not affect the automata value
                        if tile_at == None or (tile_at['layer_0'] not in self.map.impassable and nx == x and ny == y):
                            continue

                        if tile_at['layer_0'] == "OCEAN":
                            tiles -= 2
                        elif tile_at['layer_0'] == "SHORE":
                            tiles -= 1
                        elif tile_at['layer_0'] not in self.map.impassable:
                            tiles += 1
                        count += 1

                if tiles <= -(count/2) and self.map.get((x,y))['layer_0'] != "OCEAN":
                    new_map.layer_0[y][x] = 'SHORE'
                if tiles > -(count/2) and tiles < (count/2):
                    new_map.layer_0[y][x] = 'SAND'
                    # Add a small chance of adding a palm tree
                    if random.randint(0,100) < 5:
                        new_map.layer_1[y][x] = 'PALMTREE'

        self.map.layer_0 = copy.copy(new_map.layer_0)
        self.map.layer_1 = copy.copy(new_map.layer_1)


    def gen_snow(self):
        new_map = copy.deepcopy(self.map)

        for x in range(0, self.map.size[0]):
            for y in range(0, self.map.size[1]):
                snow = 0
                grass = 0
                ground = 0

                for nx in range(x-1, x+2):
                    for ny in range(y-1, y+2):
                        tile_at = self.map.get((nx,ny))
                        # If the tile is off the map, or it is not water and it is the current tile, do not affect the automata value
                        if tile_at == None or (tile_at['layer_0'] not in self.map.impassable and nx == x and ny == y):
                            continue
                        elif tile_at['layer_0'] == "SNOW":
                            snow += 1
                        elif tile_at['layer_0'] == "GROUND":
                            ground += 1
                        elif tile_at['layer_0'] == "GRASS":
                            grass += 1

                # if more than two neighbours are snow, this tile should be snow
                if snow > 2:
                    new_map.layer_0[y][x] = 'SNOW'
                # otherwise, if it is snow and is isolated, clip it
                elif self.map.get((x,y))['layer_0'] == 'SNOW':
                    new_map.layer_0[y][x] = "GROUND" if ground > grass else "GRASS"

        self.map.layer_0 = copy.copy(new_map.layer_0)
        self.map.layer_1 = copy.copy(new_map.layer_1)


    # Player start location selection
    def select_player_startpoint(self, island):

        (min_x, max_x), (min_y, max_y) = self.find_island_min_max(island)

        range_x = sorted(range(min_y, max_y), key=lambda k: random.random())
        range_y = sorted(range(min_x, max_x), key=lambda k: random.random())

        tiles = []
        start_loc = (-1,-1)
        for y in range_y:
            for x in range_x:
                tiles = self.start_location_suitability((x,y))
                start_loc = (x,y)
                break
            if len(tiles) > 0:
                break;
        if len(tiles) > 0:
            # If we've succeeded in finding a start location
            self.map.start_loc = start_loc
            for tile in tiles:
                # Clear any forests that may be in the way
                self.map.set(tile, 'layer_1', 'UI_EMPTY')

            # Draw the required tiles for the start location
            self.map.set(start_loc, 'layer_1', 'MAYORS')
            self.map.set((start_loc[0]-1,start_loc[1]+1), 'layer_1', 'ROAD')
            self.map.set((start_loc[0],start_loc[1]+1), 'layer_1', 'ROAD')
            self.map.set((start_loc[0]+1,start_loc[1]+1), 'layer_1', 'ROAD')

            # Center the map on the player location
            self.map.pos_at = (max(0,start_loc[0] - config.SCREEN_X / 2), max(0, start_loc[1] - config.SCREEN_Y / 2))

            return True
        else:
            return False

    def start_location_suitability(self, loc):
        current_tile = self.map.get(loc)
        if current_tile['layer_0'] in self.map.impassable or (self.map_type != "deserts" and current_tile['layer_0'] in ['SAND', 'SNOW']):
            return []

        tiles = []
        for y in range(loc[1]-1,loc[1]+2):
            for x in range(loc[0]-2,loc[0]+3):
                tile_at = self.map.get((x,y))
                # if any of the tiles in the required minimum space are
                if tile_at['layer_0'] in self.map.impassable or tile_at['layer_1'] == 'RIVER':
                    return []
                tiles.append((x,y))

        return tiles

    # Utility classes
    def averageRGB(self, color):
        """Averages the RGB values into a grayscale color."""
        return int((color.r + color.g + color.b) / 3)
