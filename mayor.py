import random

import pygame
import config

import math

class Mayor:
    def __init__(self, difficulty):

        self.settings = {
            'music': True,
            'sfx': True
        }

        self.money = 6000
        if difficulty == "low":
            self.money = 15000
        elif difficulty == "high":
            self.money = 2000

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


    def add_building(self, building):
        if building.type != None:
            self.buildings[building.type].append(building)

    def calc_expenses(self):
        decrease = 0.00

        decrease += 0.01 * self.roads

        for priv in self.buildings['priv']:
            decrease += priv.tax

        return decrease

    def calc_income(self):
        increase = 0.00
        job_counter = 0
        
        for res in self.buildings['r']:
            increase += res.tax

        # only jobs which have people working for them produce tax
        business = self.buildings['c'] + self.buildings['i']
        counter = 0
        while job_counter < self.population and counter < len(business):
            random.shuffle(business)
            for bus in business:
                increase += bus.tax
                job_counter += bus.jobs
                counter += 1
        return increase

    def positive_times(self):
        if self.population <= 0:
            return True

        if self.population / 2 > self.jobs:
            return False

        if self.fire_safety < self.population or self.police_safety < self.population:
            return False

        return True

    def calc(self, calc_services):


        self.population = 0
        self.jobs = 0
        
        for house in self.buildings['r']:
            self.population += house.population

        for business in self.buildings['c']:
            self.jobs += business.jobs
        for business in self.buildings['i']:
            self.jobs += business.jobs

        for priv in self.buildings['priv']:
            self.jobs += priv.jobs


        decrease = self.calc_expenses()
        increase = self.calc_income()


        if decrease < increase:
            increase = increase - decrease

            # If the city is running smoothly, add all money
            if self.positive_times():
                self.money += increase
            # Else 'punish' the player by reducing their income to 3/5th of its prior value
            else:
                self.money += increase * 0.6
        else:
            # Don't do this if they are losing money, however
            self.money -= decrease
            self.money += increase
            
        if calc_services:
            self.fire_safety = 40
            self.police_safety = 40
            for priv in self.buildings['priv']:
                if hasattr(priv, 'fire_safety'):
                    self.fire_safety += priv.fire_safety
                if hasattr(priv, 'police_safety'):
                    self.police_safety += priv.police_safety
