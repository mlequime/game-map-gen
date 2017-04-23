#!/usr/bin/python
import random

from PIL import Image
import numpy as np


class DiamondSquare:
    def __init__(self, res, corners):
        """Sets up the diamond-square generator."""
        self.map = []
        #max and minimum values
        self.res = res + 1
        self.max = self.res - 1
        self.corners = corners

        self.lowValue = 0
        self.highValue = 0

        for x in range(0, self.res):
            for y in range(0, self.res):
                self.map.append(-1)

    def get(self, xy):
        """Gets the brightness value at the coordinates supplied."""
        x, y = xy
        if x < 0 or x > self.max or y < 0 or y > self.max:
            return -1
        return self.map[x + (self.res * y)]
    def set(self, xy, value):
        x, y = xy
        self.map[x + (self.res * y)] = value

    def average(self, values):
        """Calculates the average of an input list of values if the values are greater than -1."""
        items = [i for i in values if i != -1]

        return -1 if len(items) == 0 else sum(items) / len(items)
    def divide(self, res):
        half = res / 2
        scale = self.rough * res

        if half < 1:
            return

        # Iterate recursively through square steps then diamond steps.
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

    def convert_table(self):
        output = []

        for x in range(0, self.res):
            row = []
            for y in range(0, self.res):
                val = self.map[y + (x * self.res)]
                row.append(val)
            output.append(row)

        return output

    def convert_to_image(self):
        """Convert the finished matrix to an RGB image"""
        output = []

        for x in range(0, self.res):
            row = []
            for y in range(0, self.res):
                val = (self.map[y + (x * self.res)] / self.highValue) * 255  # normalize the values to 0-255 for rgb
                row.append(val)
            output.append(row)

        array = np.asarray(output)
        im = Image.fromarray(array)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        return im