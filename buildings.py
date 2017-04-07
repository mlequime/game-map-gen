import pygame
import random
import math


class Building:
    def __init__(self, image, price, tax, type='d'):
        self.image = image
        self.price = price
        self.tax = tax
        self.type = type

class House(Building):
    def __init__(self, id="HOUSE", price=50, population=random.randint(2, 4)):
        Building.__init__(self, id, price, 2*population,'r')
        self.population = population
        self.requiredJobs = math.ceil(population / 2) if population > 3 else population

class BigHouse(House):
    def __init__(self):
        House.__init__(self, "BIGHOUSE", 75, random.randint(4, 6))


class Apartments(House):
    def __init__(self):
        House.__init__(self, "APARTMENTS", 200, random.randint(9, 20))

class Store(Building):
    def __init__(self, id='STORE', price=50, jobs=6):
        Building.__init__(self, id, price, 2*jobs, 'c')
        self.jobs = jobs

class PoliceStation(Building):
    def __init__(self, price=50, jobs=10):
        Building.__init__(self, "POLICE", price, 4*jobs, 'priv')
        self.jobs = jobs
        self.police_safety = 60

class FireStation(Building):
    def __init__(self, price=50, jobs=10):
        Building.__init__(self, "FIRE",price, 4*jobs, 'priv')
        self.jobs = jobs
        self.fire_safety = 60