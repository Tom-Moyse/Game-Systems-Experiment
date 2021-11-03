from gui_base import *
from settings import *
import pygame as pg

# TODO: ADD ammo counter for weapons somewhere

class GUIController:
    def __init__(self, game, screen, camera):
        self._game = game
        self._screen = screen
        self._camera = camera
        self._gui_surface = pg.Surface((WIDTH, HEIGHT))
        self._gui_surface.set_colorkey((0, 0, 0))
        self._elements = []

    def reset_elements(self):
        self._elements = []

    def add_elements(self, *elements, **kwargs):
        for element in elements:
            if element == "hotbar":
                self._elements.append(Hotbar(self))
            if element == "hpbar":
                self._elements.append(HPBar(self, kwargs["tracking"]))
            if element == "scorecounter":
                self._elements.append(ScoreCounter(self))
            if element == "ammocounter":
                self._elements.append(AmmoCounter(self, kwargs["tracking"]))


    def remove_elements(self, **kwargs):
        to_remove = []
        for element in self._elements:
            if type(element) is HPBar:
                if element.tracking == kwargs["tracking"]:
                    to_remove.append(element)
        for element in to_remove:
            self._elements.remove(element)
            del element

    def get_element(self, element_type):
        for element in self._elements:
            if type(element) is Hotbar and element_type == "hotbar":
                return element
            if type(element) is ScoreCounter and element_type == "scorecounter":
                return element

    def draw(self):
        self._gui_surface.fill((0, 0, 0))
        for subGUI in self._elements:
            subGUI.draw()

            if type(subGUI) == HPBar:
                if subGUI.tracking.get_visible():
                    self._gui_surface.blit(subGUI._gui_surface, [self._camera.get_offset()[0] + subGUI.x_pos_offset, self._camera.get_offset()[1] + subGUI.y_pos_offset])
            elif type(subGUI) == ScoreCounter:
                self._gui_surface.blit(subGUI._gui_surface, subGUI.get_pos())
            elif type(subGUI) == Hotbar:
                self._gui_surface.blit(subGUI._gui_surface, subGUI.get_pos())
            elif type(subGUI) == AmmoCounter:
                self._gui_surface.blit(subGUI._gui_surface, subGUI.get_pos())
            else:
                self._gui_surface.blit(subGUI._gui_surface, (0, 0))

        self._screen.blit(self._gui_surface, (0, 0))

    def get_surface(self):
        return self._gui_surface

    def event_handle(self, event_type):
        for subGUI in self._elements:
            if event_type in subGUI.important_events:
                subGUI.event_handle(event_type)


class Hotbar:
    def __init__(self, controller):
        self.controller = controller

        self.layout = GridLayout((0, 0), 1, 4)
        self.layout.add_element(InflatableRect(self, (0, 0), 40, 40, 1.2, LIGHTGREY, "pistol"), (0, 0))
        self.layout.add_element(InflatableRect(self, (0, 0), 40, 40, 1.2, LIGHTGREY), (1, 0))
        self.layout.add_element(InflatableRect(self, (0, 0), 40, 40, 1.2, LIGHTGREY), (2, 0))
        self.layout.add_element(InflatableRect(self, (0, 0), 40, 40, 1.2, LIGHTGREY), (3, 0))
        self.layout.update_elements()
        self.layout.get_element((0, 0)).set_inflated(True)
        self.layout.update_elements()

        self._gui_surface = pg.Surface((self.layout.get_width(), self.layout.get_height()))
        self._gui_surface.set_colorkey((0, 0, 0))

        self._pos = ((WIDTH - self.layout.get_width()) // 2, HEIGHT - 100)

        self.important_events = ["scroll-up", "scroll-down", "mouse-press"]
        self._selected_pos = 0

    def event_handle(self, event):
        self._gui_surface.fill((0, 0, 0))
        if event == "scroll-up":
            self._selected_pos -= 1
            if self._selected_pos < 0:
                self._selected_pos = 3
        if event == "scroll-down":
            self._selected_pos += 1
            if self._selected_pos > 3:
                self._selected_pos = 0

        for count in range(4):
            if self._selected_pos == count:
                self.layout.get_element((count, 0)).set_inflated(True)
            else:
                self.layout.get_element((count, 0)).set_inflated(False)
        self.layout.update_elements()

    def change_item(self, pos, item):
        self.layout.get_element((pos,0)).set_image(item)


    def get_selected_pos(self):
        return self._selected_pos

    def get_pos(self):
        return self._pos

    def get_surface(self):
        return self._gui_surface

    def draw(self):
        self.layout.draw()



class HPBar:
    def __init__(self, controller, tracking):
        self.controller = controller

        self._gui_surface = pg.Surface((50, 20))
        self._gui_surface.set_colorkey((0, 0, 0))

        self.tracking = tracking
        self.tracking_pos = (self.tracking.pos.x, self.tracking.pos.y)

        self.bar = Bar(self, self.tracking_pos, 50, 20, RED, GREEN)

        self.important_events = [None]

    def draw(self):
        self._gui_surface.fill((0, 0, 0))
        self.bar.set_bar_percent(self.tracking.hp / self.tracking.hp_max)
        self.x_pos_offset = self.tracking.pos.x - ((50 - self.tracking.rect.w) // 2)
        self.y_pos_offset = self.tracking.pos.y - 20 - 10
        self.bar.set_pos((0, 0))
        self.bar.draw()


class ScoreCounter:
    def __init__(self, controller):
        self.controller = controller
        self._score = 0

        self._label = Label(self, (0,0) , 200, 40, str(self._score), (0, 0, 0), WHITE)

        self._gui_surface = pg.Surface((200, 40))
        self._gui_surface.set_colorkey((0, 0, 0))

        self._pos = (WIDTH-200, 0)

        self.important_events = []

    def increment_score(self, change):
        self._score += change
        self._label.set_text(str(self._score))

    def get_surface(self):
        return self._gui_surface

    def get_score(self):
        return self._score

    def get_pos(self):
        return self._pos

    def draw(self):
        self._label.draw()


class AmmoCounter:
    def __init__(self, controller, tracking):
        self.controller = controller
        self.tracking = tracking

        self._label = Label(self, (0, 0), 200, 40, "0/0", (0, 0, 0), WHITE)

        self._gui_surface = pg.Surface((200, 40))
        self._gui_surface.set_colorkey((0, 0, 0))

        self._pos = (50, 800)

        self.important_events = []


    def get_surface(self):
        return self._gui_surface

    def get_pos(self):
        return self._pos

    def draw(self):
        self._label.set_text(f"{self.tracking._selected_weapon.get_current_mag_ammo()}/{self.tracking._selected_weapon.get_max_mag_ammo()}")
        self._label.draw()