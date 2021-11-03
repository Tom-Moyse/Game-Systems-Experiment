import random


class Gun:
    """Template weapon class that features all required methods"""
    def __init__(self, game, owner):
        self._game = game
        self._owner = owner

        self._max_mag_ammo = 0
        self._current_mag_ammo = 0
        self._fire_type = 0     # Fire type can be of following: 'auto', 'burst', 'single'
        self._fire_rate = 0     # If gun is of 'burst' type determines the fire rate within burst
        self._shot_speed = 0
        self._spread = 0        # Defines max deviation from aim angle in degrees
        self._reload_time = 0
        self._damage = 0
        self._shot_count = 0

        self._burst_timer = 0
        self._reload_timer = 0
        self._fire_timer = 0
        self._burst_counter = 0


    def shoot(self, start_pos, end_pos):
        """Method that returns all relevant information about bullet(s) that can be instantiated"""
        # Arguments stored in list as some weapons fire multiple bullets per shot
        bullets_args = []
        # Check base conditions met to allow weapon to be fired
        if self._reload_timer > 0 or self._fire_timer > 0 or self._burst_timer > 0:
            return bullets_args
        elif self._current_mag_ammo <= 0:
            return bullets_args
        else:
            # Indentifies bullet arguments based on weapon attributes
            base_direction = (end_pos - start_pos).normalize()
            # Each bullet set of arguments stored as tuple within bullet_args list
            for shot in range(self._shot_count):
                direction = base_direction.rotate(random.uniform(-self._spread, self._spread))
                bullets_args.append((self._game, start_pos.x, start_pos.y, direction*self._shot_speed,
                                     self._owner, self._damage))
            # Resets weapon firing timers and decrements weapon ammo
            self._fire_timer = 1 / self._fire_rate
            self._current_mag_ammo -= self._shot_count

            if self._fire_type == "burst":
                self._burst_counter += 1
                if self._burst_counter >= self._burst_size:
                    self._burst_timer = self._burst_rate
                    self._burst_counter = 0
        return bullets_args

    def start_reload(self):
        self._reload_timer = self._reload_time

    def update(self):
        if self._reload_timer > 0:
            self._reload_timer -= self._game.dt
        elif self._reload_timer < 0:
            self._reload_timer = 0
            self._current_mag_ammo = self._max_mag_ammo

        if self._fire_timer > 0:
            self._fire_timer -= self._game.dt
        elif self._fire_timer < 0:
            self._fire_timer = 0

        if self._burst_timer > 0:
            self._burst_timer -= self._game.dt
        elif self._burst_timer < 0:
            self._burst_timer = 0

    def get_max_mag_ammo(self):
        return self._max_mag_ammo
    def get_current_mag_ammo(self):
        return  self._current_mag_ammo


class Pistol(Gun):
    def __init__(self, game, owner, max_mag_ammo_scalar=1, fire_rate_scalar=1, spread_scalar=1, reload_time_scalar=1, shot_speed_scalar=1, damage_scalar=1):
        super().__init__(game, owner)

        self._max_mag_ammo = int(round(20 * max_mag_ammo_scalar))
        self._current_mag_ammo = self._max_mag_ammo
        self._fire_type = 'single'
        self._fire_rate = 3 * fire_rate_scalar
        self._shot_speed = 400 * shot_speed_scalar
        self._spread = 10 * spread_scalar
        self._reload_time = 2 * reload_time_scalar
        self._damage = 3 * damage_scalar
        self._shot_count = 1


class BurstPistol(Gun):
    def __init__(self, game, owner, max_mag_ammo_scalar=1, fire_rate_scalar=1, spread_scalar=1, reload_time_scalar=1,
                 burst_rate_scalar=1, burst_size_scalar=1, shot_speed_scalar=1, damage_scalar=1):
        super().__init__(game, owner)
        self._max_mag_ammo = int(round(16 * max_mag_ammo_scalar))
        self._current_mag_ammo = self._max_mag_ammo
        self._fire_type = 'burst'
        self._fire_rate = 10 * fire_rate_scalar
        self._burst_rate = 1 * burst_rate_scalar
        self._burst_size = int(round(4 * burst_size_scalar))
        self._shot_speed = 400 * shot_speed_scalar
        self._spread = 20 * spread_scalar
        self._reload_time = 2.5 * reload_time_scalar
        self._damage = 3 * damage_scalar
        self._shot_count = 1


class Shotgun(Gun):
    def __init__(self, game, owner, max_mag_ammo_scalar=1, fire_rate_scalar=1, spread_scalar=1, reload_time_scalar=1,
                 shot_speed_scalar=1, damage_scalar=1, shot_count_scalar=1):

        super().__init__(game, owner)
        self._max_mag_ammo = int(round(20 * max_mag_ammo_scalar))
        self._current_mag_ammo = self._max_mag_ammo
        self._fire_type = 'single'
        self._fire_rate = 1 * fire_rate_scalar
        self._shot_speed = 300 * shot_speed_scalar
        self._spread = 45 * spread_scalar
        self._reload_time = 3 * reload_time_scalar
        self._damage = 2 * damage_scalar
        self._shot_count = int(round(4 * shot_count_scalar))

class NoWeapon(Gun):
    def __init__(self, game, owner):
        super().__init__(game, owner)
