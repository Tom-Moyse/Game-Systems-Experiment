import pygame as pg
from settings import *


class Camera():
    def __init__(self, game, x, y, w, h):
        self.game = game
        self.pos = pg.Vector2(x, y)
        self.width = w
        self.height = h
        self.draw_offset = pg.Vector2()

    def set_pos(self, x, y):
        self.pos.x = x
        self.pos.y = y
        self._correct_pos()


    def get_offset(self):
        self.draw_offset.x = -(self.pos.x - (self.width/2))
        self.draw_offset.y = -(self.pos.y - (self.height/2))
        return self.draw_offset

    def _correct_pos(self):
        if self.pos.x < self.width/2:
            self.pos.x = self.width/2
        elif self.pos.x > self.game.map.get_pixelwidth() - (self.width/2):
            self.pos.x = self.game.map.get_pixelwidth() - (self.width/2)
        if self.pos.y < self.height/2:
            self.pos.y = self.height/2
        elif self.pos.y > self.game.map.get_pixelheight() - (self.height/2):
            self.pos.y = self.game.map.get_pixelheight() - (self.height/2)