#!/usr/bin/python
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


class DiamondSquare:
    def __init__(self, res, corners):
        self.map = []
        self.res = res + 1
        self.max = self.res - 1
        self.corners = corners

        self.lowValue = 0
        self.highValue = 0

        for x in range(0, self.res):
            for y in range(0, self.res):
                self.map.append(-1)

    def get(self, xy):
        x, y = xy
        if x < 0 or x > self.max or y < 0 or y > self.max:
            return -1
        return self.map[x + (self.res * y)]

    def set(self, xy, value):
        x, y = xy
        self.map[x + (self.res * y)] = value

    def average(self, values):
        items = [i for i in values if i != -1]

        return -1 if len(items) == 0 else sum(items) / len(items)

    def divide(self, res):
        half = res / 2
        scale = self.rough * res

        if half < 1:
            return

        for y in range(half, self.max, res):
            for x in range(half, self.max, res):
                self.square((x, y), half, random.uniform(
                    0.00, 1.00) * scale * 2 - scale)

        for y in range(0, self.max + 1, half):
            for x in range((y + half) % res, self.max + 1, res):
                self.diamond((x, y), half, random.uniform(
                    0.00, 1.00) * scale * 2 - scale)

        self.divide(res / 2, )

    def square(self, xy, res, change):
        x, y = xy

        t1 = self.get((x - res, y - res))
        t2 = self.get((x + res, y - res))
        b1 = self.get((x - res, y + res))
        b2 = self.get((x + res, y + res))
        val = self.average([t1, t2, b1, b2]) + change

        if val < self.lowValue:
            self.lowValue = val
        elif val > self.highValue:
            self.highValue = val

        self.set(xy, val)

    def diamond(self, xy, res, change):
        x, y = xy

        t = self.get((x, y - res))
        r = self.get((x + res, y))
        b = self.get((x, y + res))
        l = self.get((x - res, y))
        val = self.average([t, r, b, l]) + change

        if val < self.lowValue:
            self.lowValue = val
        elif val > self.highValue:
            self.highValue = val

        self.set(xy, val)

    def generate(self, rough):
        self.rough = rough
        self.set((0, 0), self.corners[0])
        self.set((0, self.max), self.corners[1])
        self.set((self.max, 0), self.corners[2])
        self.set((self.max, self.max), self.corners[3])

        self.divide(self.max)

        if self.lowValue > 0:
            self.lowValue = 0

        print "low value: ", self.lowValue
        for x in range(0, len(self.map)):
            self.map[x] -= self.lowValue

        self.highValue -= self.lowValue

    def convertTable(self):
        output = []

        for x in range(0, self.res):
            row = []
            for y in range(0, self.res):
                val = self.map[y + (x * self.res)]
                row.append(val)
            output.append(row)

        return output

    def convertToImage(self):
        output = []

        for x in range(0, self.res):
            row = []
            for y in range(0, self.res):
                val = (self.map[y + (x * self.res)] / self.highValue) * 255 # normalize the values to 0-255 for rgb
                row.append(val)
            output.append(row)

        array = np.asarray(output)
        im = Image.fromarray(array)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        return im

class PerlinNoise:
    def __init__(self):
        self.permutation = range(0, 256)
        random.shuffle(self.permutation)
        self.p = []
        for i in range(0, 512):
            self.p.append(self.permutation[i%256])



class MainGenerator:
    def __init__(self):
        noiselib.init(256)
        pass

    def generateStandard(self, scale, type, roughness):

        res = 2 ** scale if scale < 8 else 2 ** 8
        size = (res, res)

        # if type == "land":
        #     corners = (res - 1, res - 1, res - 1, res - 1)
        # elif type == "mixed":
        #     corners = (0, (res - 1) / 2, (res - 1) / 2, res - 1)
        # elif type == "ocean":
        #     corners = (0, 0, 0, 0)
        # else:
        #     corners = ((res - 1) / 2, (res - 1) / 2, (res - 1) / 2, (res - 1) / 2)
#
        # Produce the initial shape with the diamond-square algorithm
        #dsGenerator = DiamondSquare(res, corners)
        #dsGenerator.generate(roughness)
        #img = dsGenerator.convertToImage()

        #test = pygame.image.frombuffer(img.tobytes(), img.size, 'RGB')
        #test = pygame.transform.scale(test, size)
        #pygame.image.save(test, "test2.png")

        src = fBm(8, 0.45, simplex_noise2)
        src = RescaleNoise((-1, 1), (0, 1), src)
        colors = ((0, 0, 0), (233, 233, 233), 1)
        src = RGBLerpNoise(colors, src)

        surface = pygame.Surface((size[0]*2,size[1]*2))
        PixelArray(surface, src)

        surface = pygame.transform.smoothscale(surface, size)

        pygame.image.save(surface, "test3.png")

        return surface

    def generateIsland(self, scale):
        # Generate a standard map
        slate = self.generateStandard(scale, type, 2.5)

        # apply the mask

        slate = self.increaseContrast(slate,1.6,-10)
        slate = self.applyVMask(slate)
        pygame.image.save(slate, "slate.png")
        return slate


    def mergeImages(self, mode, *args):

        size = args[0].get_size()
        slate = pygame.Surface(size)

        for surface in args:
            if surface.get_size() != size:
                print "Sizes do not match!"

        for y in range(0, size[1]):
            row = []
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
                    slate.set_at((x,y), pygame.Color(av, av, av, 255))
                except Exception, e:
                    print av
        return slate

    def applyVMask(self, surface):
        size = surface.get_size()
        mask = pygame.Surface(size)
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                distances = x - size[0] * 0.5, y - size[1] * 0.5
                dis = math.sqrt(distances[0] ** 2 + distances[1] ** 2)

                max_w = float(size[0]) * 0.5
                delta = float(dis) / max_w
                gradient = delta * delta
                change = max(0.0, 1.0 - delta) * 2.5

                # only want to *darken* colors when applying this mask,
                # otherwise appears totally washed out
                old_color = surface.get_at((x, y)).r
                color = int(round(float(old_color * change)))
                if color > old_color:
                    color = old_color

                mask.set_at((x, y), pygame.Color(color,color,color,255))
        return mask



    def brightenImage(self, surface, factor):
        print "Brightening image by {}".format(factor)


        size = surface.get_size()

        for y in range(0, size[1]):
            for x in range(0, size[0]):
                color = surface.get_at((x,y))
                new_color =  pygame.Color(color.r * factor, color.g * factor, color.b * factor, 255)
                surface.set_at((x,y), new_color)

        pygame.image.save(surface, "slate_brighter.png")
        return surface

    def increaseContrast(self, surface, factor, brightness=0):
        print "Increasing contrast of surface"
        size = surface.get_size()


        for y in range(0, size[1]):
            for x in range (0, size[0]):
                old_color = surface.get_at((x,y)).r
                new_color = int((factor * (old_color - 128)) + 128 + brightness)
                if new_color < 0:
                    new_color = 0
                elif new_color > 255:
                    new_color = 255
                try:
                    surface.set_at((x,y), pygame.Color(new_color, new_color, new_color, 255))
                except Exception, e:
                    print new_color

        return surface