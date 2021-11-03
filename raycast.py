import pygame as pg
import pygame.gfxdraw
import math
from random import choice
from settings import *


class Ray:
    """Ray class that is used within the ray-source object"""
    def __init__(self, x1, y1, x2, y2):
        self._start_pos = pg.Vector2(x1, y1)
        self._end_pos = pg.Vector2(x2, y2)
        self._dir = self._end_pos - self._start_pos
        self._mag = 1
        self._bearing = self.calculate_bearing()

    def set_magnitude(self, new_mag):
        self._mag = new_mag
        self._end_pos = (self._dir * self._mag) + self._start_pos
        self._dir = self._end_pos - self._start_pos

    def calculate_bearing(self):
        y_change = self._dir.y
        x_change = self._dir.x
        # Abstract cases
        if x_change == 0:
            if y_change < 0:
                return 0
            else:
                return math.pi
        elif y_change == 0:
            if x_change > 0:
                return math.pi / 2
            else:
                return math.pi * 3 / 2
        # Standard cases
        if y_change < 0 and x_change > 0:
            # TOP-RIGHT QUAD RAY DIR
            return math.atan(abs(x_change) / abs(y_change))
        elif y_change > 0 and x_change > 0:
            # BOTTOM-RIGHT QUAD
            return math.atan(abs(y_change) / abs(x_change)) + (math.pi / 2)
        elif y_change > 0 and x_change < 0:
            # BOTTOM-LEFT QUAD
            return math.atan(abs(x_change) / abs(y_change)) + math.pi
        else:
            # BOTTOM-RIGHT QUAD
            return math.atan(abs(y_change) / abs(x_change)) + (math.pi * 3 / 2)

    def get_direction(self):
        return self._dir

    def get_bearing(self):
        return self._bearing

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos

    def get_distance(self):
        return self._dir.length()


class Edge:
    """Edge class that is used within the ray-source object"""
    def __init__(self, x1, y1, x2, y2):
        self._start_pos = pg.Vector2(x1, y1)
        self._end_pos = pg.Vector2(x2, y2)
        self._dir = self._end_pos - self._start_pos

    def get_direction(self):
        return self._dir

    def get_start_pos(self):
        return self._start_pos

    def get_end_pos(self):
        return self._end_pos


def _find_intersect(ray, edge):
    """Function that allows for the intersection to be found between a ray and an edge"""
    r_px = ray.get_start_pos().x
    r_py = ray.get_start_pos().y
    r_dx = ray.get_direction().x
    r_dy = ray.get_direction().y

    e_px = edge.get_start_pos().x
    e_py = edge.get_start_pos().y
    e_dx = edge.get_direction().x
    e_dy = edge.get_direction().y

    if r_dx == 0 or r_dy == 0:
        return None

    # Calculates 'distance along' the ray and edge at intersect
    t2 = (r_dx * (e_py - r_py) + r_dy * (r_px - e_px)) / (e_dx * r_dy - e_dy * r_dx)
    t1 = (e_px + e_dx * t2 - r_px) / r_dx

    # Returns magnitude of ray at intersect or None if no intersect between given ray and edge is found
    if 0 <= t2 <= 1:
        if 1 > t1 > 0:
            return t1
    else:
        return None


def _calculate_triangle_area(p1, p2, p3):
    return abs((p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2)


class RaySource:
    """Main class used to provide 'visibility' system within game via the use of 'Ray' and 'Edge' objects"""
    def __init__(self, pos, corners, edges):
        self._pos = pos
        self._corners = corners
        self._edges = edges

        self._update_rays()

    def _update_rays(self):
        self._rays = []
        for corner in self._corners:
            # Casts 3 rays to each corner: A central ray and an offset ray to either side by 0.01 rads
            ray_central = Ray(self._pos.x, self._pos.y, corner[0], corner[1])
            ray_offset1 = self._gen_offset_ray(ray_central, 0.01)
            ray_offset2 = self._gen_offset_ray(ray_central, -0.01)
            ray_offset1.set_magnitude(50)
            ray_offset2.set_magnitude(50)
            self._rays.append(ray_central)
            self._rays.append(ray_offset1)
            self._rays.append(ray_offset2)

        self._order_rays()

    def _gen_offset_ray(self, ray, offset):
        """Calculates the parameters to generate a ray at a given angle offset from another
        And returns the ray generated via these parameters"""
        y_change = ray.get_direction().y
        x_change = ray.get_direction().x
        if y_change < 0 and x_change > 0:
            quad = "TR"
            angle = ray.get_bearing()

        elif y_change > 0 and x_change > 0:
            quad = "BR"
            angle = math.pi - ray.get_bearing()

        elif y_change > 0 and x_change < 0:
            quad = "BL"
            angle = ray.get_bearing() - math.pi
        else:
            quad = "TL"
            angle = (2 * math.pi) - ray.get_bearing()

        angle += offset
        # Calculate change in x and y based on new angle
        x_change = math.sin(angle) * ray.get_distance()
        y_change = math.cos(angle) * ray.get_distance()

        # Calculate new end position of ray based upon quadrant ray is situated in
        if quad == "TR":
            end_x = ray.get_start_pos().x + x_change
            end_y = ray.get_start_pos().y - y_change
        elif quad == "BR":
            end_x = ray.get_start_pos().x + x_change
            end_y = ray.get_start_pos().y + y_change
        elif quad == "BL":
            end_x = ray.get_start_pos().x - x_change
            end_y = ray.get_start_pos().y + y_change
        else:
            end_x = ray.get_start_pos().x - x_change
            end_y = ray.get_start_pos().y - y_change

        return Ray(ray.get_start_pos().x, ray.get_start_pos().y, end_x, end_y)

    def _order_rays(self):
        """Orders rays in list based upon their bearing via a selection sort"""
        self.ordered_rays = []

        for i in range(len(self._rays)):
            min_bearing = 10
            for ray in self._rays:
                if ray.get_bearing() < min_bearing:
                    min_bearing = ray.get_bearing()
                    min_ray = ray
            self._rays.remove(min_ray)
            self.ordered_rays.append(min_ray)
        self._rays = self.ordered_rays

    def _update_intersects(self):
        """Uses the find intersect method to find the shortest given intersect for all rays
        And updates rays accordingly"""
        for ray in self._rays:
            max_t1 = None

            # Loops through each edge to find closest edge that intersects the ray
            for edge in self._edges:
                t1 = _find_intersect(ray, edge)
                if max_t1 is None:
                    max_t1 = t1
                elif t1 is not None:
                    if t1 < max_t1:
                        max_t1 = t1
            # Sets magnitude of ray such that it touches closest edge
            if max_t1 is not None:
                ray.set_magnitude(max_t1)

    def check_visible(self, pos):
        """Tests if a given point is located within the visible regions outlined by the rays"""
        for i in range(len(self._rays)):
            point1 = round(self._pos.x), round(self._pos.y)
            point2 = round(self._rays[i - 1].get_end_pos().x), round(self._rays[i - 1].get_end_pos().y)
            point3 = round(self._rays[i].get_end_pos().x), round(self._rays[i].get_end_pos().y)

            big_a = round(_calculate_triangle_area(point1, point2, point3))
            a1 = round(_calculate_triangle_area(pos, point2, point3))
            a2 = round(_calculate_triangle_area(point1, pos, point3))
            a3 = round(_calculate_triangle_area(point1, point2, pos))

            if abs(a1 + a2 + a3 - big_a) < 5:
                return True
        return False

    def draw_visible_regions(self, screen, cam_offset):
        """Draws green coloured overlay on screen to show player the visible/not visible regions"""
        x_ofs = cam_offset[0]
        y_ofs = cam_offset[1]
        for i in range(len(self._rays)):
            pg.gfxdraw.filled_trigon(screen, round(self._pos.x + x_ofs), round(self._pos.y + y_ofs),
                                     round(self._rays[i - 1].get_end_pos().x + x_ofs),
                                     round(self._rays[i - 1].get_end_pos().y + y_ofs),
                                     round(self._rays[i].get_end_pos().x + x_ofs),
                                     round(self._rays[i].get_end_pos().y + y_ofs), GREEN)

    def update(self, new_pos, new_corners, new_edges):
        """Method called when either position needs to be updated or corners/edges have changed"""
        self._pos = new_pos
        self._corners = new_corners
        self._edges = new_edges
        self._update_rays()
        self._update_intersects()
