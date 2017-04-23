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

    def can_place(self, tile_at, map=None):
        """By default, all buildings can be provided they are near road. Can be overridden with specific use cases."""
        True

    def locked(self, player):
        """By default, all buildings are unlocked. Can be overridden with specific use cases."""
        return False

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

    def locked(self, player):
        return player.population < 100


class Apartments(House):
    """A large block of apartments."""
    def __init__(self):
        House.__init__(self, "APARTMENTS", 1200, random.randint(12, 20))

    def locked(self, player):
        return player.population < 500

class Store(Building):
    """A commercial shop."""
    def __init__(self, id='STORE', price=400, jobs=6):
        Building.__init__(self, id, price, 3*jobs, 'c')
        self.jobs = jobs


class BigStore(Store):
    """A commercial shop."""
    def __init__(self, id='STORE', price=800, jobs=24):
        Store.__init__(self, id, price, jobs)

    def locked(self, player):
        return player.population < 400

class PoliceStation(Building):
    """A police station, a required building based on population."""
    def __init__(self, price=50, jobs=10):
        Building.__init__(self, "POLICE", price, 12*jobs, 'priv')
        self.jobs = jobs
        self.police_safety = 170

    def locked(self, player):
        return player.population < 50

class FireStation(Building):
    """A fire station, a required building based on population."""
    def __init__(self, price=50, jobs=10):
        Building.__init__(self, "FIRE",price, 12*jobs, 'priv')
        self.jobs = jobs
        self.fire_safety = 150

    def locked(self, player):
        return player.population < 50

class CoalMine(Building):
    def __init__(self):
        Building.__init__(self, "MINE", 1200, 45, 'i')
        self.jobs = 20

    def can_place(self, tile_at, map=None):
        return tile_at['tile']['layer_0'] in ['GROUNDCOAL','GRASSCOAL','SANDCOAL']

class OilRig(Building):
    def __init__(self):
        Building.__init__(self, "MINE", 3500, 80, 'i')
        self.jobs = 60

    def can_place(self, tile_at, map=None):
        return tile_at['tile']['layer_0'] in ['GROUNDOIL','GRASSOIL','SANDOIL','WATEROIL']

    def locked(self, player):
        return player.population < 200


class FerryTerminal(Building):
    def __init__(self):
        Building.__init__(self, "FERRY", 1000, 50, 'priv')
        self.jobs = 5

    def can_place(self, tile_at, map=None):
        x,y = tile_at['map_xy']
        place = False
        # If there is a shoreline within a single tile, it can be placed
        if (x > 0 and map.get(((x-1), y))['layer_0'] == 'SHORE') or \
            (x < map.size[0] - 1 and map.get((x+1, y))['layer_0'] == 'SHORE') or \
                (y > 0 and map.get((x,y-1))['layer_0'] == 'SHORE') or \
                (y < map.size[1] - 1 and map.get((x, y+1))['layer_0'] == 'SHORE'):
            place = True
        return place

    def locked(self, player):
        return player.population < 400