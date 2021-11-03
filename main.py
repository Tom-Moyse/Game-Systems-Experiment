import pygame as pg
from os import environ
from sys import exit
from camera import *
from tilemap import *
from gui import *
from raycast import *
from screens import *
from settings import *
from math import sqrt
import time


def end():
    pg.quit()
    exit()

def test_save(game):
    with open("saves/save.dat", "wb") as file:
        pickle.dump(game, file)
    file.close()

class Timer:
    def __init__(self):
        self._time_elapsed = 0
        self._timestamp = 0

    def start_timer(self):
        self._timestamp = time.time()

    def stop_timer(self):
        self._time_elapsed += time.time() - self._timestamp
        self._timestamp = time.time()

    def reset_timer(self):
        self.__init__()

    def get_time(self):
        return self._time_elapsed


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.mixer = pg.mixer.init()
        self._s_heal = pg.mixer.Sound("sfx/heal.wav")
        self._s_heal.set_volume(1)
        self.db = databaseController()

    def new_game(self):
        self._comp_diff_score = 1
        self._time_diff_score = 1
        self._level_timer = Timer()
        self._game_timer = Timer()
        self._damage_diff_adjustments = []
        self.new_level()

    def end_level(self):
        self._game_timer.stop_timer()
        self._level_timer.stop_timer()

        time_score = round(60 - self._level_timer.get_time())
        if time_score < 0:
            time_score = 0
        print("Previous score:",self.gui.get_element("scorecounter").get_score())
        print("Time score:",time_score)
        print("Level completion score:",20)
        self.gui.get_element("scorecounter").increment_score(time_score)
        self.gui.get_element("scorecounter").increment_score(20)
        print("New score:", self.gui.get_element("scorecounter").get_score())
        total_time = self._game_timer.get_time()
        self._time_diff_score = (120 + total_time)/120
        percent_damage = 1 - (self.player.hp / self.player.hp_max)
        damage_diff_adjust = -(2/3) * math.tan((2*percent_damage) - 1)

        self._damage_diff_adjustments.append(damage_diff_adjust)

        self._comp_diff_score = sum(self._damage_diff_adjustments) + self._time_diff_score

        for enemy in self.enemies:
            enemy.destroy()
        self.player.destroy()

        self.show_score_screen()

    def next_level(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.crates = pg.sprite.Group()
        self.exit = None
        self.player = None
        self.map = Map()
        self.map.load_tilemap(self)
        self.prev_room = None
        self.ray_source = RaySource(self.player.get_pos(), [], [])
        self.wall_surface = pg.Surface((self.map.get_pixelwidth(), self.map.get_pixelheight()))
        self.wall_surface.fill(DARKGREY)

        self.all_sprites.add(self.player)
        for enemy in self.enemies:
            self.all_sprites.add(enemy)
            self.gui.add_elements("hpbar", tracking=enemy)
        self.gui.add_elements("hpbar", tracking=self.player)

        self.walls.update()
        for wall in self.walls:
            self.wall_surface.blit(wall.image, wall.rect)

        self.run()


    def new_level(self):
        # initialize all variables and do all the setup for a new game
        self.visibilitySurface = pg.Surface((WIDTH, HEIGHT))
        self.visibilitySurface.set_alpha(32)
        if DEBUG:
            self.visibilitySurface.set_alpha(180)
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.crates = pg.sprite.Group()
        self.exit = None
        self.player = None
        self.map = Map()
        self.map.load_tilemap(self)
        self.prev_room = None
        self.camera = Camera(self, self.player.pos.x, self.player.pos.y, WIDTH, HEIGHT)
        self.gui = GUIController(self, self.screen, self.camera)
        self.ray_source = RaySource(self.player.get_pos(), [], [])
        self.wall_surface = pg.Surface((self.map.get_pixelwidth(), self.map.get_pixelheight()))
        self.wall_surface.fill(DARKGREY)

        self.all_sprites.add(self.player)
        for enemy in self.enemies:
            self.all_sprites.add(enemy)
            self.gui.add_elements("hpbar", tracking=enemy)

        self.gui.add_elements("hpbar", tracking=self.player)
        self.gui.add_elements("hotbar")
        self.gui.add_elements("scorecounter")
        self.gui.add_elements("ammocounter", tracking=self.player)

        self.walls.update()
        for wall in self.walls:
            self.wall_surface.blit(wall.image, wall.rect)


    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self._game_timer.start_timer()
        self._level_timer.start_timer()
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            if self.dt > 0.1: self.dt = 0.1
            self.inputs()
            self.update()
            self.draw()


    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.set_pos(self.player.get_pos().x, self.player.get_pos().y)


        current_room = self.map.get_room_or_corridor((self.player.get_center_pos().x, self.player.get_center_pos().y))
        if current_room != self.prev_room:
            # Player has moved to a new room
            self.near_rooms = set(self.map.get_connected_rooms_corridors((self.player.get_center_pos().x, self.player.get_center_pos().y)))
            self.near_rooms.add(current_room)

            # Set enemies to be active/inactive
            for enemy in self.enemies:
                enemy_room = self.map.get_room_or_corridor((enemy.get_center_pos().x, enemy.get_center_pos().y))
                enemy.set_active(enemy_room in self.near_rooms)
                enemy.set_to_path(enemy_room in self.near_rooms and enemy_room != current_room)


            near_room_copy = set([i for i in self.near_rooms])
            for room in near_room_copy:
                pos = self.map._get_random_pos(room)
                temp_store = self.map.get_connected_rooms_corridors((pos[0]*TILESIZE, pos[1]*TILESIZE))
                for item in temp_store:
                    self.near_rooms.add(item)

            # Update raytracing corners and edges as appropriate
            self.near_corners = []
            self.near_edges = []
            for room in self.near_rooms:
                self.corners = get_corners(room)
                edges = get_edges(self.corners)
                for edge in edges:
                    self.near_edges.append(edge)
                for corner in self.corners:
                    self.near_corners.append(corner)

            self.near_edges = separate_edges(self.near_edges)

        self.ray_source.update(self.player.get_center_pos(), self.near_corners, self.near_edges)
        self.prev_room = current_room


    def draw(self):
        if DEBUG:
            color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
            self.screen.fill(color)
            self.visibilitySurface.fill(color)
        else:
            self.screen.fill(BGCOLOUR)
            self.visibilitySurface.fill(BGCOLOUR)

        cam_offset = self.camera.get_offset()
        self.screen.blit(self.wall_surface, cam_offset)
        for sprite in self.all_sprites:
            if type(sprite) == Enemy:
                if not self.ray_source.check_visible(tuple(sprite.get_pos())):
                    sprite.set_visible(False)
                    continue
                sprite.set_visible(True)
            if sprite.get_visible():
                self.screen.blit(sprite.image, sprite.rect.move(cam_offset))

        self.gui.draw()
        self.ray_source.draw_visible_regions(self.visibilitySurface, cam_offset)

        self.screen.blit(self.visibilitySurface, (0,0))
        if DEBUG:
            for edge in self.near_edges:
                x_pos_s = edge.get_start_pos()[0] + cam_offset[0]
                y_pos_s = edge.get_start_pos()[1] + cam_offset[1]
                x_pos_e = edge.get_end_pos()[0] + cam_offset[0]
                y_pos_e = edge.get_end_pos()[1] + cam_offset[1]
                pg.draw.line(self.screen, (random.randint(0,255),random.randint(0,255),random.randint(0,255)), (x_pos_s,y_pos_s), (x_pos_e,y_pos_e),5)

        if DEBUG:
            for enemy in self.enemies:
                if enemy._active:
                    path = enemy._path
                    if path is not None:
                        for node in path._data:
                            rect = pg.Rect((node[0]*TILESIZE, node[1]*TILESIZE),(32,32))
                            rect = rect.move(cam_offset)

                            pg.draw.rect(self.screen, BLUE, rect)
                        rect = pg.Rect((enemy._current_target[0] * TILESIZE, enemy._current_target[1] * TILESIZE), (32, 32))
                        rect = rect.move(cam_offset)

                        pg.draw.rect(self.screen, MAGENTA, rect)


        if DEBUG:
            if SHOWGRIDLINES:
                for x in range(0, WIDTH, TILESIZE):
                    pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
                for y in range(0, HEIGHT, TILESIZE):
                    pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))
        pg.display.flip()

    def inputs(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.show_pause_screen()
                if event.key == pg.K_e:
                    self.check_interactions()
                if event.key == pg.K_r:
                    self.player._selected_weapon.start_reload()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.gui.event_handle("scroll-up")
                if event.button == 5:
                    self.gui.event_handle("scroll-down")
        if pg.mouse.get_pressed()[0]:
            self.player.attack()

    def show_start_screen(self):
        StartScreen(self)

    def show_login_screen(self):
        LoginScreen(self)

    def show_leaderboard_screen(self):
        LeaderboardScreen(self)

    def show_pause_screen(self):
        self._level_timer.stop_timer()
        self._game_timer.stop_timer()
        PauseScreen(self)

    def show_score_screen(self):
        ScoreScreen(self)

    def show_settings_screen(self):
        SettingsScreen(self)

    def show_end_screen(self):
        EndScreen(self)

    def check_interactions(self):
        for crate in self.crates:
            distance = sqrt((crate.rect.x - self.player.pos.x)**2 + (crate.rect.y - self.player.pos.y)**2)
            if distance < 100:
                crate.open()
                crate.destroy()
        exit_distance = sqrt((self.exit.rect.x - self.player.pos.x)**2 + (self.exit.rect.y - self.player.pos.y)**2)
        if exit_distance < 100:
            self.exit.interact()

    def game_loop(self):
        self.new_game()
        self.run()

    def get_time_diff(self):
        return self._time_diff_score

    def get_comp_diff(self):
        return self._comp_diff_score


environ['SDL_VIDEO_CENTERED'] = '1'

# create the game object
g = Game()
g.show_start_screen()


