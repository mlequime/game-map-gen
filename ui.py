import pygame

import buildings
import config
import map
import mayor

from mayor import Mayor


class MenuScreen:
    """The menu screen where the user selects the action they would like to take"""

    def __init__(self, screen, callback):
        self.screen = screen

        pygame.mixer.init()

        self.title_music = pygame.mixer.Sound("src/title.ogg")

        self.bg = pygame.image.load("src/title_bg.png").convert_alpha()
        self.logo = pygame.image.load("src/nations.png").convert_alpha()

        button_bg = []
        button_bg.append(pygame.image.load("src/title_option.png").convert_alpha())
        button_bg.append(pygame.image.load("src/title_option_hover.png").convert_alpha())

        self.new_button = TitleButton("New Game", None, button_bg)
        self.exit_button = TitleButton("Quit Nations", None, button_bg)

        self.callback = callback

    def open(self):
        # Play the title music
        self.title_music.play(-1)

        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.bg, (0, 0))
            # Center the logo in the middle of the screen
            self.screen.blit(self.logo, (((config.SCREEN_X * config.TILE_W) / 2) + config.SIDEBAR_WIDTH - \
                                         (self.logo.get_rect().width / 2), 100))

            self.new_button.draw(self.screen, 300)
            self.exit_button.draw(self.screen, 350)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if pygame.mouse.get_pressed()[0]:
                    if self.new_button.rect.collidepoint(pygame.mouse.get_pos()):
                        # self.close()
                        self.callback(self.screen, 'config', True)
                    elif self.exit_button.rect.collidepoint(pygame.mouse.get_pos()):
                        exit()

            pygame.display.flip()

    def close(self):
        if hasattr(self, 'tile_music'):
            self.title_music.fadeout(50)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class TitleButton:
    """Class to represent a button on the title screen"""

    def __init__(self, text, action, button_bg):
        self.action = action
        self.text = text
        self.width = 400
        self.bg, self.bg_hov = button_bg

    def draw(self, screen, posY):
        offsetX = screen.get_size()[0] / 2 - self.width / 2
        self.rect = pygame.Rect(offsetX, posY, self.width, self.bg.get_size()[1])
        for i in range(0, self.width / 2):
            # blit the button (with the hover background if the mouse is over it)
            screen.blit(self.bg_hov if self.rect.collidepoint(pygame.mouse.get_pos()) else self.bg,
                        (i * 2 + offsetX, posY))
            # render the text as a label and blit it in the center of the button
            label = config.FONT.render(self.text, 1, (0, 0, 0))
            screen.blit(label, (offsetX + (self.width / 2 - label.get_size()[0] / 2), posY + 8))


class ConfigureScreen:
    """The map configuration screen, where a user will set up the map that they want to play on."""

    def __init__(self, screen, callback):
        self.screen = screen
        self.callback = callback
        self.bg = pygame.image.load("src/title_bg.png").convert_alpha()

        self.map_types = {}
        self.rainfall_types = {}
        self.resource_types = {}
        self.size_types = {}
        self.difficulty_types = {}

        self.map_type = "island"
        self.resource_type = "medium"
        self.rainfall_type = "medium"
        self.size_type = "medium"
        self.difficulty_type = "medium"

    def open(self):
        def set(var, value):
            setattr(self, var, value)

        self.map_types = {
            'island': {
                'label': config.FONT.render("Island", 1, pygame.Color("white")),
                'button': RadioButton(True, lambda: set('map_type', "island"))
            },
            'continents': {
                'label': config.FONT.render("Continents", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('map_type', "continents"))
            },
            'highlands': {
                'label': config.FONT.render("Highlands", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('map_type', "highlands"))
            },
            'deserts': {
                'label': config.FONT.render("Desert Islands", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('map_type', "deserts"))
            }

        }
        self.rainfall_types = {
            'high': {
                'label': config.FONT.render("Very Rainy", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('rainfall_type', 'high'))
            },
            'medium': {
                'label': config.FONT.render("Average", 1, pygame.Color("white")),
                'button': RadioButton(True, lambda: set('rainfall_type', 'medium'))
            },
            'low': {
                'label': config.FONT.render("Very Dry", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('rainfall_type', 'low'))
            }
        }

        self.resource_types = {
            'high': {
                'label': config.FONT.render("Abundant", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('resource_type', 'high'))
            },
            'medium': {
                'label': config.FONT.render("Average", 1, pygame.Color("white")),
                'button': RadioButton(True, lambda: set('resource_type', 'medium'))
            },
            'low': {
                'label': config.FONT.render("Scare", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('resource_type', 'low'))
            }
        }
        self.size_types = {
            'high': {
                'label': config.FONT.render("Small", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('size_type', 'high'))
            },
            'medium': {
                'label': config.FONT.render("Medium", 1, pygame.Color("white")),
                'button': RadioButton(True, lambda: set('size_type', 'medium'))
            },
            'low': {
                'label': config.FONT.render("Large (May take longer to load)", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('size_type', 'low'))
            }
        }
        self.difficulty_types = {
            'high': {
                'label': config.FONT.render("Easy", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('difficulty_type', 'high'))
            },
            'medium': {
                'label': config.FONT.render("Average", 1, pygame.Color("white")),
                'button': RadioButton(True, lambda: set('difficulty_type', 'medium'))
            },
            'low': {
                'label': config.FONT.render("Difficult", 1, pygame.Color("white")),
                'button': RadioButton(False, lambda: set('difficulty_type', 'low'))
            }
        }

        button_bg = []
        button_bg.append(pygame.image.load("src/title_option.png").convert_alpha())
        button_bg.append(pygame.image.load("src/title_option_hover.png").convert_alpha())

        self.generate_button = TitleButton("Generate", None, button_bg)

        clock = pygame.time.Clock()
        while True:

            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if pygame.mouse.get_pressed()[0]:
                    self.click(event.pos)

            self.draw(self.screen)
            pygame.display.flip()

    def click(self, pos):
        for item, value in self.map_types.iteritems():
            button = value['button']
            label = value['label']
            if button == None or button.rect == None:
                continue
            if button.rect.collidepoint(pos):
                button.on_click()
        for item, value in self.rainfall_types.iteritems():
            button = value['button']
            label = value['label']
            if button == None or button.rect == None:
                continue
            if button.rect.collidepoint(pos):
                button.on_click()

        for item, value in self.resource_types.iteritems():
            button = value['button']
            label = value['label']
            if button == None or button.rect == None:
                continue
            if button.rect.collidepoint(pos):
                button.on_click()

        for item, value in self.size_types.iteritems():
            button = value['button']
            label = value['label']
            if button == None or button.rect == None:
                continue
            if button.rect.collidepoint(pos):
                button.on_click()

        for item, value in self.difficulty_types.iteritems():
            button = value['button']
            label = value['label']
            if button == None or button.rect == None:
                continue
            if button.rect.collidepoint(pos):
                button.on_click()

        if self.generate_button.rect.collidepoint(pos):
            # When clicking the generate button
            values = ["low", "medium", "high"]
            data = {
                'map': self.map_type,
                # Convert into integers
                'rainfall': values.index(self.rainfall_type),
                'resources': values.index(self.resource_type),
                'size': values.index(self.size_type),
                'difficulty': values.index(self.difficulty_type)
            }
            self.callback(self.screen, 'game', True, data)

    def draw(self, screen):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.bg, (0, 0))

        # Draw first column
        start_pos = (100, 50)
        bottom = 50

        map_type_header = config.TITLE_FONT.render("Map Type:", 1, pygame.Color("white"))

        bottom = self.draw_list(self.map_type, map_type_header, self.map_types, start_pos)

        # Draw second column
        start_pos = (config.SCREEN_SIZE[0] / 2 + 10, start_pos[1])

        rainfall_header = config.TITLE_FONT.render("Rainfall:", 1, pygame.Color("white"))
        second_bottom = self.draw_list(self.rainfall_type, rainfall_header, self.rainfall_types, start_pos)

        bottom = max(bottom, second_bottom)

        # Draw first column of second row
        start_pos = (100, bottom + 20)

        resource_header = config.TITLE_FONT.render("Resources:", 1, pygame.Color("white"))
        bottom = self.draw_list(self.resource_type, resource_header, self.resource_types, start_pos)

        # Draw second column
        start_pos = (config.SCREEN_SIZE[0] / 2 + 10, start_pos[1])

        size_header = config.TITLE_FONT.render("Map Size:", 1, pygame.Color("white"))
        second_bottom = self.draw_list(self.size_type, size_header, self.size_types, start_pos)

        bottom = max(bottom, second_bottom)

        # Draw first column of third row
        start_pos = (100, bottom + 50)

        difficulty_header = config.TITLE_FONT.render("Difficulty:", 1, pygame.Color("white"))
        bottom = self.draw_list(self.difficulty_type, difficulty_header, self.difficulty_types, start_pos)

        self.generate_button.draw(self.screen, config.SCREEN_SIZE[1] - 100)

    def draw_list(self, data, header, list, start_pos):

        self.screen.blit(header, start_pos)
        start_pos = (start_pos[0], start_pos[1] + header.get_rect().height + 10)

        for key, item in list.iteritems():
            item['button'].draw(self.screen, (start_pos[0], start_pos[1] + 2), key == data)
            self.screen.blit(item['label'], (start_pos[0] + 20, start_pos[1]))
            start_pos = (start_pos[0], start_pos[1] + item['label'].get_rect().height + 10)

        return start_pos[1]

    def close(self):
        pass


class RadioButton:
    def __init__(self, on, on_click):
        bg = pygame.image.load("src/ui.png").convert_alpha()
        self.bg = {
            "off": bg.subsurface(pygame.Rect(0, 0, 12, 12)),
            "on": bg.subsurface(pygame.Rect(12, 0, 12, 12))
        }
        self.on_click = on_click
        self.rect = None

    def draw(self, screen, loc, on=False):
        self.rect = pygame.Rect(loc[0], loc[1], 12, 12)
        screen.blit(self.bg['on'] if on else self.bg['off'], loc)


class GameScreen:
    """Class to represent the in-game screen once the player has initialized the game"""

    def __init__(self, screen, callback, data):
        # set up UI
        self.screen = screen
        self.screen.fill((205, 255, 255))

        # set up player
        self.player = Mayor(data['difficulty'])

        # set up Map
        tileset = map.Tileset("src/test.png")
        self.map = map.Map(tileset, (80, 40), data)

        # set up inventory
        self.inventory = [
            Purchasable("ROAD", "Road", None, 100),
            Purchasable("HOUSE", "Small House", buildings.House()),
            Purchasable("BIGHOUSE", "Large House", buildings.BigHouse()),
            Purchasable("APARTMENTS", "Apartments", buildings.Apartments()),
            Purchasable("STORE", "Store", buildings.Store()),
            Purchasable("BIGSTORE", "Big Store", buildings.BigStore()),
            Purchasable("POLICE", "Police Station", buildings.PoliceStation()),
            Purchasable("FIRE", "Fire Station", buildings.FireStation()),
            Purchasable("MINE", "Coal Mine (Can only place on coal)", buildings.CoalMine()),
            Purchasable("OILRIG", "Oil Rig (Can only place on oil)", buildings.OilRig()),
            Bulldozer()
        ]

        self.map.selected_item = self.inventory[0]

        pygame.mixer.quit()
        pygame.mixer.init()

        self.sounds = {
            'place': pygame.mixer.Sound("src/place.wav"),
            'delete': pygame.mixer.Sound("src/destroy.wav"),
            'siren': pygame.mixer.Sound("src/siren.wav"),
            'notify': pygame.mixer.Sound("src/notification.wav"),
            'broke': pygame.mixer.Sound("src/broke.wav")
        }


    def open(self):
        clock = pygame.time.Clock()

        count = 0

        # Main game loop
        while True:
            # Keep a consistent clock time even if frame rate varies
            clock.tick(30)

            count += 1

            # every cycle of 100 loops, calculate population and income
            if count % 100 == 0:
                self.player.calc(False)

            # every cycle of 300 loops, calculate safety services
            if count >= 300:
                self.player.calc(True)
                count = 0

            # Interaction loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if pygame.mouse.get_pressed()[0]:
                    self.click(event.pos)

                # Controls for moving the map
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.map.move('down')
                    if event.key == pygame.K_LEFT:
                        self.map.move('left')
                    if event.key == pygame.K_RIGHT:
                        self.map.move('right')
                    if event.key == pygame.K_UP:  # up ke
                        self.map.move('up')

            # Draw the screen and flip the pixels
            self.draw()
            pygame.display.flip()

    def close(self):
        """Function to be run when the game screen is closed."""
        pass

    def draw(self):
        """Clear the screen and draw the UI. To be run every cycle."""
        self.screen.fill((0, 0, 0))
        try:
            # Draw the map and any relevant UI
            self.map.draw(self.screen, (0, 0))

            # If there's an active tile, draw its details
            if self.map.tile_at != None:
                text = "{}: ({}, {})".format(self.map.tile_at['coords'], self.map.tile_at['tile']['layer_0'],
                                             self.map.tile_at['tile']['layer_1'] if self.map.tile_at['tile'][
                                                                                        'layer_1'] != 'UI_EMPTY' else 'None')
                tile_at_shadow = config.FONT.render(text, 1, pygame.Color("black"))
                tile_at_text = config.FONT.render(text, 1, pygame.Color("white"))

                self.screen.blit(tile_at_shadow, (config.SIDEBAR_WIDTH + 9, config.SCREEN_SIZE[1] - 17))
                self.screen.blit(tile_at_text, (config.SIDEBAR_WIDTH + 8, config.SCREEN_SIZE[1] - 18))

            # Draw the game screen interface

            # The player's money
            money = config.FONT.render("${:+.2f}".format(self.player.money), 1,
                                       config.COLOR_G if self.player.money > 0 else config.COLOR_R)
            self.screen.blit(money, (self.screen.get_size()[0] - money.get_size()[0] - 10, 4))

            # The game population
            population = config.FONT.render(
                "Population: {} | Jobs: {}".format(self.player.population, self.player.jobs), 1, (245, 245, 245))
            self.screen.blit(population, (self.screen.get_size()[0] / 2 - population.get_size()[0] / 2, 4))

            # The police and fire safety statuses
            police_safety = config.FONT.render(
                "Police: {}".format("Good" if self.player.police_safety >= self.player.population else "Bad"), 1,
                config.COLOR_G if self.player.police_safety >= self.player.population else config.COLOR_R)
            fire_safety = config.FONT.render(
                "Fire Safety: {}".format("Good" if self.player.fire_safety >= self.player.population else "Bad"), 1,
                config.COLOR_G if self.player.fire_safety >= self.player.population else config.COLOR_R)

            self.screen.blit(police_safety, (4, 4))
            self.screen.blit(fire_safety, (4 + police_safety.get_size()[0] + 20, 4))

            # Start point for inventory drawing (this is incremented in the loop)
            x = 4
            y = 22

            # Draw the inventory
            for item in self.inventory:
                rect = pygame.Rect(x, y, 24, 24)
                pygame.draw.rect(self.screen, (200, 200, 200) if self.map.selected_item != item else (255, 255, 55),
                                 rect)

                icon = self.map.tileset.get(item.ID)

                # If we've not unlocked the building yet, don't draw the icon and present the locked hover label
                if item.building != None and item.building.locked(self.player):
                    icon.convert_alpha()
                    icon.set_alpha(50)
                    self.screen.blit(self.map.tileset.get("UI_LOCKED"), (x, y))

                    if rect.collidepoint(pygame.mouse.get_pos()):
                        pygame.draw.rect(self.screen, (255, 255, 55), rect, 1)
                        # Show a label indicating the item is currently locked
                        locked = config.FONT.render("[Locked]", 1, config.COLOR_GRAY)

                        pygame.draw.rect(self.screen, (50, 50, 50), (x + 30, y, locked.get_rect().width + 10, 18))
                        self.screen.blit(locked, (x + 35, y + 2))
                else:
                    # If we are hovering over the current inventory item
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        pygame.draw.rect(self.screen, (255, 255, 55), rect, 1)
                        # Show a label with the item ID and price (if a price exists)
                        item_and_price = config.FONT.render(
                            "{}{}".format(item.text, " (${})".format(item.price) if item.price > 0 else ""), 1,
                            pygame.Color("white") if self.player.money > item.price else config.COLOR_R)

                        pygame.draw.rect(self.screen, (0, 0, 0), (x + 30, y, item_and_price.get_rect().width + 10, 18))
                        self.screen.blit(item_and_price, (x + 35, y + 2))
                    self.screen.blit(icon, (x, y))
                item.coords = (x, y)
                y += 30

        except Exception, e:
            print e.message
            exit()

    def click(self, pos):
        """Process clicks in the UI at a given position."""
        for item in self.inventory:
            if item.coords == None:
                pass
            elif pygame.Rect(item.coords[0], item.coords[1], config.TILE_W, config.TILE_H).collidepoint(pos):
                if item.building != None and item.building.locked(self.player):
                    return
                self.map.destroy = item.ID == 'BULLDOZER'
                self.map.selected_item = item

        for tile in self.map.visible_tiles:
            if tile['coords'][0] + config.TILE_W > pos[0] > tile['coords'][0] \
                    and tile['coords'][1] + config.TILE_H > pos[1] > tile['coords'][1]:
                if item.building != None and not item.building.can_place(tile['map_xy']):
                    return
                self.add_to_tile(tile['map_xy'])

    def play_sound(self, sound):
        """Plays a sound from the UI sound library, if it exists"""
        if self.player.settings['sfx'] and sound in self.sounds:
            self.sounds[sound].stop()
            self.sounds[sound].play()

    def add_to_tile(self, tile_xy):
        x, y = tile_xy
        map_at = self.map.get(tile_xy)
        # if bulldozer selected
        if self.map.selected_item.ID == 'BULLDOZER':
            if map_at['layer_1'] not in ['UI_EMPTY', 'RIVER', 'MAYORS']:
                if map_at['layer_1'] == 'ROAD':
                    self.player.roads -= 1
                self.map.set(tile_xy, 'layer_1', 'UI_EMPTY')
                self.play_sound('delete')
                self.player.money -= 20
        elif self.player.money < self.map.selected_item.price:
            self.play_sound('broke')
            return
        elif self.map.selected_item.building != None and not self.map.selected_item.building.can_place(map_at):
            return
        elif self.map.add_to_tile(tile_xy):
            # stop the player from placing a building if they can't afford it
            self.play_sound('place')
            self.player.money -= self.map.selected_item.price
            if self.map.selected_item.building != None:
                self.player.add_building(self.map.selected_item.building)
            if self.map.selected_item.ID == 'ROAD':
                self.player.roads += 1


class Purchasable:
    """Represents a purchasable item from the left-hand side catalogue."""

    def __init__(self, ID, text, building, price=None, requirement=True):
        self.ID = ID
        self.text = text
        self.building = building
        self.price = building.price if building != None else price
        self.coords = None
        self.requirement = requirement


class Bulldozer(Purchasable):
    """Represents the in-game bulldozer, which appears in the catalogue of items but has a completely custom
    behaviour."""

    def __init__(self):
        Purchasable.__init__(self, 'BULLDOZER', 'Destroy', None, None)
        self.coords = None
