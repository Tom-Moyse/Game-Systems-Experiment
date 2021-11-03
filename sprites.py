import pygame as pg
from settings import *
from pathfind import *
from weapons import *
import random
import math


class GenericSprite(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.pos = pg.Vector2(x, y)
        self.center_pos = pg.Vector2(x + (self.rect.width//2), y + (self.rect.height//2))
        self._visible = True

    def get_pos(self):
        return self.pos

    def get_center_pos(self):
        return self.center_pos

    def get_visible(self):
        return self._visible

    def set_visible(self, boolean):
        self._visible = boolean

    def update(self):
        self.rect.x = self.pos.x * TILESIZE
        self.rect.y = self.pos.y * TILESIZE


class Bullet(GenericSprite):
    """Projectile-type class that is capable of dealing 'damage' to sprites"""
    def __init__(self, game, x, y, vel, source, damage):
        super().__init__(game, x, y)
        self.image = pg.Surface((10, 10))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.vel = vel
        self.source = source
        self.damage = damage

    def _collides_with(self, x, y):
        """Identify if a bullet has collided with either a wall/enemy or player"""
        for wall in self.game.walls:
            if wall.rect.y - self.rect.h < y < wall.rect.y + wall.rect.h:
                if wall.rect.x - self.rect.w < x < wall.rect.x + wall.rect.w:
                    return wall
        # If bullet shot by player will not be able to damage player
        if type(self.source) is Player:
            for enemy in self.game.enemies:
                if enemy.rect.y - self.rect.h < y < enemy.rect.y + enemy.rect.h:
                    if enemy.rect.x - self.rect.w < x < enemy.rect.x + enemy.rect.w:
                        return enemy
        # If bullet shot by enemy will not be able to damage enemies
        elif type(self.source) is Enemy:
            if self.game.player.rect.y - self.rect.h < y < self.game.player.rect.y + self.game.player.rect.h:
                if self.game.player.rect.x - self.rect.w < x < self.game.player.rect.x + self.game.player.rect.w:
                    return self.game.player
        return None

    def update(self):
        self.pos.x += self.vel.x * self.game.dt
        self.pos.y += self.vel.y * self.game.dt
        collision = self._collides_with(self.pos.x, self.pos.y)
        if collision is not None:
            if type(collision) is not Wall:
                collision.damage(self.damage)
            self.kill()
            del self
            return
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y


class Player(GenericSprite):
    """Sprite that is controlled by player"""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.image = pg.image.load("sprites/player.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.vel = pg.Vector2(0, 0)
        self.hp = 10
        self.hp_max = 10
        # Weapons are initialised in weapons list, each element in list corresponds to a hotbar position
        self.weapons = [Pistol(self.game, self), NoWeapon(self.game, self),
                        NoWeapon(self.game, self), NoWeapon(self.game, self)]
        self._selected_weapon = self.weapons[0]
        self._damage_timer = 0


    def _set_vel(self):
        # Sets velocity based upon current player inputs
        self.vel.update(0, 0)

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x -= PLAYERSPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x += PLAYERSPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y -= PLAYERSPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y += PLAYERSPEED

        # Prevents diagonal movement from being faster
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def _collision_correct(self, axis):
        """Checks in both axis to see if a collision has occured and offsets as appropriate"""
        # Collision is handled seperately for each axis as this allows player to 'slide' along a wall
        if axis == 'x':
            wall = self._collides_with_wall(self.pos.x, self.pos.y)
            if wall is not None:
                if DEBUG: self._collides_with_wall(self.pos.x, self.pos.y).image.fill(RED)
                if self.vel.x > 0:
                    self.pos.x = wall.rect.x - self.rect.w
                elif self.vel.x < 0:
                    self.pos.x = wall.rect.x + wall.rect.w
            self.rect.x = self.pos.x

        if axis == 'y':
            wall = self._collides_with_wall(self.pos.x, self.pos.y)
            if wall is not None:
                if DEBUG: self._collides_with_wall(self.pos.x, self.pos.y).image.fill(RED)
                if self.vel.y > 0:
                    self.pos.y = wall.rect.y - self.rect.h
                elif self.vel.y < 0:
                    self.pos.y = wall.rect.y + wall.rect.h
            self.rect.y = self.pos.y

    def _collides_with_wall(self, x, y):
        """Tests if player has collided with any given wall"""
        for wall in self.game.walls:
            if wall.rect.y - self.rect.h < y < wall.rect.y + wall.rect.h:
                if wall.rect.x - self.rect.w < x < wall.rect.x + wall.rect.w:
                    return wall
        return None


    def _check_enemy_collisions(self):
        """Check and handle player collisions with enemies"""
        self._damage_timer -= self.game.dt
        collisions = []
        for enemy in self.game.enemies:
            if enemy.rect.y - self.rect.h < self.pos.y < enemy.rect.y + enemy.rect.h:
                if enemy.rect.x - self.rect.w < self.pos.x < enemy.rect.x + enemy.rect.w:
                    collisions.append(enemy)

        for enemy in collisions:
            if self._damage_timer <= 0:
                self.damage(5)
                self._damage_timer = 2

    def move(self):
        self._set_vel()
        self.pos.x += self.vel.x * self.game.dt
        self._collision_correct('x')
        self.pos.y += self.vel.y * self.game.dt
        self._collision_correct('y')
        self.center_pos.x = self.pos.x + (self.rect.width//2)
        self.center_pos.y = self.pos.y + (self.rect.height // 2)

    def attack(self):
        """Method that fires a 'Bullet' from the player to mouse location"""
        mouse_pos = pg.mouse.get_pos()
        mouse_pos_offset = self.game.camera.get_offset()
        mouse_pos_fix = mouse_pos - mouse_pos_offset
        # Handle different types of weapons as well as multiple potential shots
        bullets_args = self._selected_weapon.shoot(self.center_pos, mouse_pos_fix)
        for arg_set in bullets_args:
            bullet = Bullet(*arg_set)
            self.game.bullets.add(bullet)

    def damage(self, damage):
        self.hp -= damage
        if self.hp <=0:
            self.game.show_end_screen()

    def destroy(self):
        self.game.gui.remove_elements(tracking=self)
        self.kill()
        del self
        return

    def update(self):
        self.move()
        self._check_enemy_collisions()
        selected_slot = self.game.gui.get_element("hotbar").get_selected_pos()
        self._selected_weapon = self.weapons[selected_slot]
        self._selected_weapon.update()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.walls
        super().__init__(self.groups)
        self.game = game
        self.image = pg.image.load("sprites/wall.png").convert()
        self.rect = self.image.get_rect()
        self.pos = pg.Vector2(x, y)

    def update(self):
        self.rect.x = self.pos.x * TILESIZE
        self.rect.y = self.pos.y * TILESIZE


class Crate(GenericSprite):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.image = pg.image.load("sprites/crate.png").convert()

    def gen_random_gun(self):
        weapon_type = random.randint(0,2)
        args = self.gen_weapon_args()
        if weapon_type == 0:
            new_weapon = Pistol(self.game, self.game.player, **args)
            self.game.player.weapons[0] = new_weapon
            self.game.gui.get_element("hotbar").change_item(0,"pistol")
        elif weapon_type == 1:
            args["burst_rate_scalar"] = random.uniform(0.8,1.2)
            args["burst_size_scalar"] = random.uniform(0.8,1.2)
            new_weapon = BurstPistol(self.game, self.game.player, **args)
            self.game.player.weapons[1] = new_weapon
            self.game.gui.get_element("hotbar").change_item(1,"burstpistol")
        elif weapon_type == 2:
            args["shot_count_scalar"] = random.uniform(0.5,1.5)
            new_weapon = Shotgun(self.game, self.game.player, **args)
            self.game.player.weapons[2] = new_weapon
            self.game.gui.get_element("hotbar").change_item(2,"shotgun")



    def gen_weapon_args(self):
        return {
            "max_mag_ammo_scalar":random.uniform(0.8,1.2)*self.game._time_diff_score,
            "fire_rate_scalar":random.uniform(0.8,1.2)*self.game._time_diff_score,
            "spread_scalar":random.uniform(0.8,1.2)*self.game._time_diff_score,
            "reload_time_scalar":random.uniform(0.8,1.2)*self.game._time_diff_score,
            "shot_speed_scalar":random.uniform(0.8,1.2)*self.game._time_diff_score,
            "damage_scalar":random.uniform(0.8,1.2)*self.game._time_diff_score
        }

    def health_restore(self):
        self.game.player.hp = self.game.player.hp_max
        self.game._s_heal.play()

    def open(self):
        ran_num = random.random()
        if ran_num < 0.4:
            #health restore
            self.health_restore()
        else:
            #new weapon
            self.gen_random_gun()

    def destroy(self):
        self.kill()
        del self
        return


class Stair(GenericSprite):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.image = pg.image.load("sprites/stairs.png").convert()

    def interact(self):
        self.game.end_level()


class Enemy(GenericSprite):
    count = 0
    spaces_occupied = {}

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        Enemy.count += 1
        self.id = Enemy.count
        Enemy.spaces_occupied[self.id] = None
        self.image = pg.image.load("sprites/enemy.png").convert_alpha()
        self.hp = round(5*math.sqrt(game.get_comp_diff()))
        self.hp_max = round(5*math.sqrt(game.get_comp_diff()))
        self.dir = pg.Vector2(0, 0)
        self.vel = pg.Vector2(0, 0)
        self.speed = round(200*math.sqrt(game.get_comp_diff()))

        self._active = False
        self._visible = False
        self._to_path = False

        self._current_room = self.game.map.get_room_or_corridor(self.center_pos)

        self._path = None
        self._current_target = None

        self.default_invalid_targets = None
        self._weapon = Pistol(self.game, self, max_mag_ammo_scalar=100, fire_rate_scalar=0.4, shot_speed_scalar=0.6, damage_scalar=0.6)

    def move_to_player(self):
        if self._path is None:
            self._path = self.path_to_player()

        if self._current_target is None:
            try:
                self._current_target = self._path.pop()
            except:
                self._to_path = False

        if self.check_next_tile_target(self.center_pos, self._current_target, 10):
            if self._path.length() != 0:
                self._current_target = self._path.pop()
            else:
                self._to_path = False

        if self._to_path:
            target_pos = approximate_center_pos(self._current_target)
            self.vel.x = target_pos[0] - self.center_pos.x
            self.vel.y = target_pos[1] - self.center_pos.y
            self.vel = self.vel.normalize()

            self.vel *= self.speed

        else:
            self.vel.x = 0
            self.vel.y = 0


    def check_next_tile_target(self, enemy_pos, target_tile_pos, deviation):
        target_pos = approximate_center_pos(target_tile_pos)

        if abs(enemy_pos.x - target_pos[0]) <= deviation and abs(enemy_pos.y - target_pos[1]) <= deviation:
            return True
        else:
            return False

    def select_target_pos(self):
        base_pos = approximate_tile_pos(self.game.player)
        while True:
            x_deviation = random.randint(-2,2)
            y_deviation = random.randint(-2,2)
            test_pos = (base_pos[0] + x_deviation)*32, (base_pos[1] + y_deviation)*32
            if not self.check_space_occupied(test_pos):
                if self.game.map.get_room_or_corridor(test_pos) != False:
                    Enemy.spaces_occupied[self.id] = test_pos
                    return test_pos[0]/32, test_pos[1]/32

    def path_to_player(self):
        test_pos = self.select_target_pos()
        self.router = Pathfinder(approximate_tile_pos(self), test_pos, self.game.map.get_data_map())
        while not self.router.is_valid_path():
            room = self.game.map.get_room_or_corridor((test_pos[0]*32,test_pos[1]*32))

            self.router = Pathfinder(approximate_tile_pos(self), self.select_target_pos(), self.game.map.get_data_map())
        path = self.router.get_shortest_route()
        return path

    def check_space_occupied(self, tile_pos):
        for kv_pair in Enemy.spaces_occupied.items():
            if self.id == kv_pair[0] and tile_pos == kv_pair[1]:
                return False
            elif tile_pos == kv_pair[1]:
                return True
        return False

    def damage(self, damage):
        self.hp -= damage
        self.check_death()

    def check_death(self):
        if self.hp <= 0:
            self.game.gui.remove_elements(tracking=self)
            self.game.gui.get_element("scorecounter").increment_score(10)
            self.kill()
            del self
            return

    def destroy(self):
        self.game.gui.remove_elements(tracking=self)
        self.kill()
        del self
        return

    def attack(self):
        bullets_args = self._weapon.shoot(self.pos, self.game.player.pos)
        for arg_set in bullets_args:
            bullet = Bullet(*arg_set)
            self.game.bullets.add(bullet)

    def set_active(self, new_bool):
        self._active = new_bool

    def set_to_path(self, new_bool):
        self._to_path = new_bool
        if self._to_path:
            self._path = None


    def update(self):
        if self.default_invalid_targets is None:
            self.default_invalid_targets = [(int(wall.pos.x), int(wall.pos.y)) for wall in self.game.walls]
        if self._active:
            self.move_to_player()
            self._weapon.update()
            self.attack()
            self.pos.x += self.vel.x * self.game.dt
            self.pos.y += self.vel.y * self.game.dt
            self.center_pos.x += self.vel.x * self.game.dt
            self.center_pos.y += self.vel.y * self.game.dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y


def approximate_tile_pos(sprite):
    return sprite.center_pos.x // TILESIZE, sprite.center_pos.y//TILESIZE
def approximate_center_pos(tile_pos):
    return (tile_pos[0] * TILESIZE) + TILESIZE//2, (tile_pos[1] * TILESIZE) + TILESIZE//2


def get_tile_distance(pos1, pos2):
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])


def get_adjacent_positions(pos):
    if pos is None:
        return [None]
    adjacents = []
    offsets = ((1, 0), (0, -1), (-1, 0), (0, 1))
    for offset in offsets:
        x_pos = int(pos[0]) + offset[0]
        y_pos = int(pos[1]) + offset[1]
        adjacents.append((x_pos,y_pos))
    return adjacents


