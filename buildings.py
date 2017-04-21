import pygame
import random
import math


class Building:
    """A purchasable and placeable building on the map."""
    def __init__(self, image, price, tax, type='d'):
        # The image to use for the building both on map and in inventory
        self.image = image
        # How much the building should cost the user
        self.price = price
        # The tax revenue (or cost)
        self.tax = tax
        # The type of building ('r' for residential', 'c' for stores, 'i' for industry and 'priv' for civic service
        # buildings
        self.type = type

    def can_place(self, tile_at):
        return True

class House(Building):
    """A basic small house."""
    def __init__(self, id="HOUSE", price=400, population=random.randint(2, 4)):
        Building.__init__(self, id, price, 3*population,'r')
        self.population = population
        self.requiredJobs = math.ceil(population / 2) if population > 3 else population

class BigHouse(House):
    """A basic larger house."""
    def __init__(self):
        House.__init__(self, "BIGHOUSE", 600, random.randint(4, 6))


class Apartments(House):
    """A large block of apartments."""
    def __init__(self):
        House.__init__(self, "APARTMENTS", 1200, random.randint(12, 20))

class Store(Building):
    """A commercial shop."""
    def __init__(self, id='STORE', price=400, jobs=6):
        Building.__init__(self, id, price, 3*jobs, 'c')
        self.jobs = jobs

class PoliceStation(Building):
    """A police station, a required building based on population."""
    def __init__(self, price=50, jobs=10):
        Building.__init__(self, "POLICE", price, 8*jobs, 'priv')
        self.jobs = jobs
        self.police_safety = 60

class FireStation(Building):
    """A fire station, a required building based on population."""
    def __init__(self, price=50, jobs=10):
        Building.__init__(self, "FIRE",price, 8*jobs, 'priv')
        self.jobs = jobs
        self.fire_safety = 60

class CoalMine(Building):
    def __init__(self):
        Building.__init__(self, "MINE", 200, 10, 'i')

    def can_place(self, tile_at):
        return tile_at['layer_0'] in ['GROUNDCOAL','GRASSCOAL','SANDCOAL']

class OilRig(Building):
    def __init__(self):
        Building.__init__(self, "MINE", 200, 10, 'i')

    def can_place(self, tile_at):
        return tile_at['layer_0'] in ['GROUNDOIL','GRASSOIL','SANDOIL','WATEROIL']