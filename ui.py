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
        # self.title_music.play(-1)

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
                        self.callback(self.screen, 'game', True)
                    elif self.exit_button.rect.collidepoint(pygame.mouse.get_pos()):
                        exit()

            pygame.display.flip()

    def close(self):
        self.title_music.fadeout(50)
        pygame.mixer.quit()
        del self.bg
        del self.logo
        del self.title_music
        print("closing")

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


class GameScreen:
    """Class to represent the in-game screen once the player has initialized the game"""

    def __init__(self, screen, callback):
        # set up UI
        self.screen = screen
        self.screen.fill((205, 255, 255))

        pygame.mixer.init()

        self.sounds = {
            'place': pygame.mixer.Sound("src/place.wav"),
            'delete': pygame.mixer.Sound("src/destroy.wav"),
            'siren': pygame.mixer.Sound("src/siren.wav"),
            'notify': pygame.mixer.Sound("src/notification.wav"),
            'broke': pygame.mixer.Sound("src/broke.wav")
        }

        # set up player
        self.player = Mayor("easy")

        # set up Map
        tileset = map.Tileset("src/test.png")
        self.map = map.Map(tileset, (80, 40))

        self.inventory = [
            Purchasable("ROAD", "Road", None, 100),
            Purchasable("HOUSE", "Small House", buildings.House()),
            Purchasable("BIGHOUSE", "Large House", buildings.BigHouse()),
            Purchasable("APARTMENTS", "Apartments", buildings.Apartments()),
            Purchasable("STORE", "Store", buildings.Store()),
            Purchasable("POLICE", "Police Station", buildings.PoliceStation()),
            Purchasable("FIRE", "Fire Station", buildings.FireStation()),
            Purchasable("MINE", "Coal Mine", buildings.CoalMine()),
            Purchasable("OILRIG", "Oil Rig", buildings.OilRig()),
            Bulldozer()
        ]

        # Allow placing of special items for debug purposes
        if config.DEBUG:
            self.inventory.append(Purchasable("RIVER", "River", None, 0))
            self.inventory.append(Purchasable("TREES", "Forest", None, 0))
            self.inventory.append(Purchasable("SHORE", "Shore", None, 0))

            self.inventory.append(Purchasable("GRASSCOAL", "Coal", None, 0))
            self.inventory.append(Purchasable("GRASSOIL", "Oil", None, 0))


        self.selected_item = self.inventory[0]

    def open(self):
        clock = pygame.time.Clock()

        count = 0

        while True:
            clock.tick(30)
            count += 1

            # every cycle of 400 frames, calculate safety services
            if count >= 400:
                self.player.calculate(True)
                count = 0

            # every cycle of 200 frames, calculate population and income
            if count % 200 == 0:
                self.player.calculate(False)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if pygame.mouse.get_pressed()[0]:
                    try:
                        self.click(event.pos)
                    except AttributeError:
                        pass

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.map.move('down')
                    if event.key == pygame.K_LEFT:
                        self.map.move('left')
                    if event.key == pygame.K_RIGHT:
                        self.map.move('right')
                    if event.key == pygame.K_UP:  # up ke
                        self.map.move('up')

            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

    def close(self):
        pass

    def draw(self):
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
            money = config.FONT.render("${}".format(self.player.money), 1,
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

            for item in self.inventory:
                rect = pygame.Rect(x, y, 24, 24)
                pygame.draw.rect(self.screen, (200, 200, 200) if self.selected_item != item else (255, 255, 55), rect)

                # If we are hovering over the current inventory item
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (255, 255, 55), rect, 1)
                    # Show a label with the item ID and price (if a price exists)
                    item_and_price = config.FONT.render(
                        "{}{}".format(item.text, " (${})".format(item.price) if item.price > 0 else ""), 1,
                        pygame.Color("white") if self.player.money > item.price else config.COLOR_R)

                    pygame.draw.rect(self.screen, (0, 0, 0), (x + 30, y, item_and_price.get_rect().width + 10, 18))
                    self.screen.blit(item_and_price,(x + 35, y + 2))

                icon = self.map.tileset.get(item.ID)
                self.screen.blit(icon, (x, y))
                item.coords = (x, y)
                y += 30

        except Exception, e:
            print e.message
            exit()

    def click(self, pos):
        for item in self.inventory:
            if item.coords == None:
                pass
            elif pygame.Rect(item.coords[0], item.coords[1], config.TILE_W, config.TILE_H).collidepoint(pos):
                self.map.destroy = item.ID == 'BULLDOZER'
                self.selected_item = item
                self.map.selected_item = item

        for tile in self.map.visible_tiles:
            if tile['coords'][0] + config.TILE_W > pos[0] > tile['coords'][0] \
                    and tile['coords'][1] + config.TILE_H > pos[1] > tile['coords'][1]:
                self.add_to_tile(tile['map_xy'])

    def play_sound(self, sound):
        if self.player.settings['sfx'] and sound in self.sounds:
            self.sounds[sound].stop()
            self.sounds[sound].play()

    def add_to_tile(self, tile_xy):
        x, y = tile_xy
        # if bulldozer selected
        if self.selected_item.ID == 'BULLDOZER':
            map_at = self.map.get(tile_xy)['layer_1']
            if map_at not in ['UI_EMPTY', 'RIVER', 'MAYORS']:
                if map_at == 'ROAD':
                    self.player.roads -= 1
                self.map.set(tile_xy, 'layer_1', 'UI_EMPTY')
                self.play_sound('delete')
                self.player.money -= 20
        elif self.player.money < self.map.selected_item.price:
            self.play_sound('broke')
            return
        elif self.map.add_to_tile(tile_xy):
            # stop the player from placing a building if they can't afford it
            self.play_sound('place')
            self.player.money -= self.map.selected_item.price
            if self.map.selected_item.building != None:
                self.player.addBuilding(self.map.selected_item.building)
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
