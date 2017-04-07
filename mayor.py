import pygame
import config

import math

class Mayor:
    def __init__(self, difficulty):

        self.settings = {
            'music': True,
            'sfx': True
        }

        self.money = 5000
        if difficulty == "easy":
            self.money = 10000
        elif difficulty == "hard":
            self.money = 2500

        self.fire_safety = 1
        self.police_safety = 1

        self.population = 0
        self.jobs = 0
        self.tourism_factor = 0.05

        self.buildings = {
            'r': [],
            'c': [],
            'i': [],
            'priv': []
        }

        self.roads = 0


    def addBuilding(self, building):
        if building.type != None:
            self.buildings[building.type].append(building)

    def calculateExpenses(self):
        expense = 0.00

        expense += 0.01 * self.roads

        for priv in self.buildings['priv']:
            expense += priv.tax

        self.money -= expense

    def calculateIncome(self):
        increase = 0.00

        for res in self.buildings['r']:
            increase += res.tax

        for com in self.buildings['c']:
            increase += com.tax

        self.money += increase

    def calculate(self, calculate_services):
        self.calculateExpenses()
        self.calculateIncome()
        self.population = 0
        self.jobs = 0
        for house in self.buildings['r']:
            self.population += house.population

        for business in self.buildings['c']:
            self.jobs += business.jobs
        for priv in self.buildings['priv']:
            self.jobs += priv.jobs

        if calculate_services:
            self.fire_safety = 40
            self.police_safety = 40
            for priv in self.buildings['priv']:
                if hasattr(priv, 'fire_safety'):
                    self.fire_safety += priv.fire_safety
                if hasattr(priv, 'police_safety'):
                    self.police_safety += priv.police_safety
