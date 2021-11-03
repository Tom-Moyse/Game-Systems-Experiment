from settings import *
from sprites import *
from levelgen import LevelGenerator
from raycast import Edge
import random
import math


def lower(a, b):
    if a < b:
        return a
    else:
        return b


class AdjacencyMatrix:
    """Functions as boolean array to inform whether any given node is connected
    /adjacent to any other given node. As well can be used to determine adjacent nodes and edges"""

    def __init__(self, nodes, edges):
        self._nodes = nodes
        self._edges = edges
        # Order of nodes in rows and columns mirrors order in list attribute nodes
        self._matrix = [[False for c1 in range(len(nodes))] for c2 in range(len(nodes))]
        self._fill_matrix()

    def _fill_matrix(self):
        """Private method that initialises the matrix with values pertaining to input nodes and edges"""
        for edge in self._edges:
            node1 = edge.get_left_room()
            node2 = edge.get_right_room()
            pos1 = self._nodes.index(node1)
            pos2 = self._nodes.index(node2)
            self._matrix[pos1][pos2] = True
            self._matrix[pos2][pos1] = True

    def get_adjacent_nodes(self, node):
        """Returns all nodes adjacent to the input node"""
        adjacencies = self._matrix[self._nodes.index(node)]
        adjacent_nodes = []
        for count in range(len(adjacencies)):
            if adjacencies[count]:
                adjacent_nodes.append(self._nodes[count])
        return adjacent_nodes

    def get_connected_edges(self, node):
        """Returns all edges connected to a given node"""
        connected_edges = []
        for edge in self._edges:
            node1 = edge.get_left_room()
            node2 = edge.get_right_room()
            if node == node1 or node == node2:
                connected_edges.append(edge)
        return connected_edges

    def get_connected_nodes(self, edge):
        """Returns nodes that are conected to a given edge"""
        return edge.get_right_room(), edge.get_left_room()

    def test_adjacent(self, node1, node2):
        """Returns True/False to query if two given nodes are adjacent"""
        index1 = self._nodes.index(node1)
        index2 = self._nodes.index(node2)
        return self._matrix[index1][index2]


def get_corners(room):
    tile_corners = [(room.get_x() + 1, room.get_y() + 1),
                    (room.get_end_x(), room.get_y() + 1),
                    (room.get_end_x(), room.get_end_y()),
                    (room.get_x() + 1, room.get_end_y())]
    pixel_corners = []
    for corner in tile_corners:
        pixel_corners.append((corner[0] * TILESIZE, corner[1] * TILESIZE))
    return pixel_corners


def get_edges(corners):
    edges = []
    for count in range(len(corners)):
        edge = Edge(corners[count - 1][0], corners[count - 1][1], corners[count][0], corners[count][1])
        edges.append(edge)
    return edges


def _find_overlap_edges(edges):
    """Returns a list of overlaps where each element in the list is a list of two or more edges
    The first element in each of said list is the long edge (the room edge)
    The following elements in list are corridor edges sorted by order of start pos
    Where left most element is that of the furthest left/up edge start position"""
    overlaps = []
    has_overlapped = []
    check_list = [*edges]

    # Runs until all edges have been checked for overlaps
    while len(check_list) != 0:
        # Initialises variable to test for overlap
        overlap = False
        edge1 = check_list[0]
        e1_dir = edge1.get_direction()

        # Iterates over all remaining edges that have not yet been checked
        for edge_count in range(1, len(check_list)):
            edge2 = check_list[edge_count]
            e2_dir = edge2.get_direction()

            # Test if two edges are both travelling vertically and share a horizontal x start position
            if e1_dir.x == 0 and e2_dir.x == 0 and edge1.get_start_pos().x == edge2.get_start_pos().x:
                # Finds which edge is longer and assigns to variables as appropriate
                long_edge = edge2
                short_edge = edge1
                if e1_dir.y > e2_dir.y:
                    long_edge = edge1
                    short_edge = edge2
                l_srt = long_edge.get_start_pos()
                s_srt = short_edge.get_start_pos()

                # Check if the two edges overlap
                if l_srt.y < s_srt.y and long_edge.get_end_pos().y > short_edge.get_end_pos().y:
                    # If long edge has not overlapped with any other edges append the pair of edges to overlaps list
                    if long_edge not in has_overlapped:
                        overlaps.append([long_edge, short_edge])
                    # Otherwise find's the edges existing overlap pair and appends new edge to the list
                    else:
                        for index, overlap in enumerate(overlaps):
                            if overlap[0] == long_edge:
                                overlap_index = index
                                break
                        # Edges are placed in length order within the overlap list
                        if overlaps[overlap_index][1].get_start_pos().y < s_srt.y:
                            overlaps[overlap_index].append(short_edge)
                        else:
                            overlaps[overlap_index].insert(1, short_edge)
                    # Removes the short edge from the check list
                    check_list.remove(short_edge)
                    overlap = True
                    # Add long edge to the has overlapped list
                    has_overlapped.append(long_edge)
                    # Returns to outer loop
                    break

            # Test if two edges are both travelling horizontally and share a vertical y start position
            elif e1_dir.y == 0 and e2_dir.y == 0 and edge1.get_start_pos().y == edge2.get_start_pos().y:
                # Finds which edge is longer and assigns to variables as appropriate
                long_edge = edge2
                short_edge = edge1
                if e1_dir.x > e2_dir.x:
                    long_edge = edge1
                    short_edge = edge2
                l_srt = long_edge.get_start_pos()
                s_srt = short_edge.get_start_pos()

                # Check if the two edges overlap
                if l_srt.x < s_srt.x and long_edge.get_end_pos().x > short_edge.get_end_pos().x:
                    # If long edge has not overlapped with any other edges append the pair of edges to overlaps list
                    if long_edge not in has_overlapped:
                        overlaps.append([long_edge, short_edge])
                    # Otherwise find's the edges existing overlap pair and appends new edge to the list
                    else:
                        for index, overlap in enumerate(overlaps):
                            if overlap[0] == long_edge:
                                overlap_index = index
                                break
                        # Edges are placed in length order within the overlap list
                        if overlaps[overlap_index][1].get_direction().x < short_edge.get_direction().x:
                            overlaps[overlap_index].insert(1, short_edge)
                        else:
                            overlaps[overlap_index].append(short_edge)
                    # Removes the short edge from the check list
                    check_list.remove(short_edge)
                    overlap = True
                    # Add long edge to the has overlapped list
                    has_overlapped.append(long_edge)
                    # Returns to outer loop
                    break

        # If no overlap between edges remove current inspected edge from the check list
        if not overlap:
            check_list.remove(edge1)

    # Return all identified overlapping edge groups
    return overlaps


def separate_edges(edges):
    # Initialise final_edges to be all edges
    final_edges = edges
    overlaps = _find_overlap_edges(edges)
    # Remove any overlapping edges from list of final_edges
    for overlap in overlaps:
        for edge in overlap:
            final_edges.remove(edge)

    # Iterates over each overlap group found
    for overlap in overlaps:
        # Check if overlap featured vertical edges
        if overlap[0].get_direction().x == 0:
            # Initialise key points with the start pos of first edge in overlap list (which is the long edge)
            key_points = [overlap[0].get_start_pos().y]
            # For all remaining edges in the overlap list, append start and end points to key_points list
            # In order from highest point to lowest point
            for overlap_edge in overlap[1:]:
                p1 = overlap_edge.get_start_pos().y
                p2 = overlap_edge.get_end_pos().y
                if p1 < p2:
                    key_points.append(p1)
                    key_points.append(p2)
                else:
                    key_points.append(p2)
                    key_points.append(p1)
            key_points.append(overlap[0].get_end_pos().y)

            # Instantiate new edges for each pair of key points in key_points list
            # Where first point in pair represents start point of new edge and second represents end point of new edge
            # Append instantiated edge to list of final_edges
            for kp_count in range(0, len(key_points), 2):
                srt_pt_y = key_points[kp_count]
                end_pt_y = key_points[kp_count + 1]
                if srt_pt_y != end_pt_y:
                    x_pos = overlap[0].get_start_pos().x
                    final_edges.append(Edge(x_pos, srt_pt_y, x_pos, end_pt_y))

        # If overlap featured horizontal edges
        else:
            # Initialise key points with the start pos of first edge in overlap list (which is the long edge)
            key_points = [overlap[0].get_start_pos().x]
            # For all remaining edges in the overlap list, append start and end points to key_points list
            # In order from highest point to lowest point
            for overlap_edge in overlap[1:]:
                p1 = overlap_edge.get_start_pos().x
                p2 = overlap_edge.get_end_pos().x
                if p1 < p2:
                    key_points.append(p1)
                    key_points.append(p2)
                else:
                    key_points.append(p2)
                    key_points.append(p1)
            key_points.append(overlap[0].get_end_pos().x)

            # Instantiate new edges for each pair of key points in key_points list
            # Where first point in pair represents start point of new edge and second represents end point of new edge
            # Append instantiated edge to list of final_edges
            for kp_count in range(0, len(key_points), 2):
                srt_pt_x = key_points[kp_count]
                end_pt_x = key_points[kp_count + 1]
                if srt_pt_x != end_pt_x:
                    y_pos = overlap[0].get_start_pos().y
                    final_edges.append(Edge(srt_pt_x, y_pos, end_pt_x, y_pos))

    # Returns all the final edges which now feature no overlapping edges
    return final_edges

class Map:
    def __init__(self):
        self._tilewidth = 60
        self._tileheight = 50

        self._generator = LevelGenerator(self._tilewidth, self._tileheight, 3, 0.2)
        self._generator_rooms = self._generator.get_rooms()
        self._generator_corridors = self._generator.get_corridors()
        self.adjust_corridors()
        self._adjacent_matrix = AdjacencyMatrix(self._generator_rooms, self._generator_corridors)

        self._map_layout = self._generator.get_layout()

        self._pixelwidth = self._tilewidth * TILESIZE
        self._pixelheight = self._tileheight * TILESIZE

    def adjust_corridors(self):
        """Dimensions of corridors have to be adjusted from the level generator to be more easily useable"""
        for corridor in self._generator_corridors:
            if corridor.get_direction() == "V":
                corridor.set_y(corridor.get_y() - 1)
                corridor.set_end_y(corridor.get_end_y() + 1)
                corridor.set_height(corridor.get_height() + 2)
            else:
                corridor.set_x(corridor.get_x() - 1)
                corridor.set_end_x(corridor.get_end_x() + 1)
                corridor.set_width(corridor.get_width() + 2)

    def load_tilemap(self, game):
        player_room = random.choice(self._generator_rooms)
        player_pos_x = player_room.get_x() + (player_room.get_width() - 2) / 2
        player_pos_y = player_room.get_y() + (player_room.get_height() - 2) / 2
        game.player = Player(game, player_pos_x * TILESIZE, player_pos_y * TILESIZE)

        self._load_walls(game)

        stair_pos = self._get_random_pos(random.choice(self._generator_rooms))
        game.exit = Stair(game, stair_pos[0], stair_pos[1])
        game.all_sprites.add(game.exit)
        self._load_internals(game)

    def get_data_map(self):
        return self._map_layout

    def get_pixelwidth(self):
        return self._pixelwidth

    def get_pixelheight(self):
        return self._pixelheight

    def get_tilewidth(self):
        return self._tilewidth

    def get_tileheight(self):
        return self._tileheight

    def get_current_room(self, pos):
        """Returns the room that encloses any given pos"""
        tile_pos = pos[0] // TILESIZE, pos[1] // TILESIZE
        for room in self._generator_rooms:
            if room.get_x() < tile_pos[0] < room.get_end_x():
                if room.get_y() < tile_pos[1] < room.get_end_y():
                    return room
        return False

    def get_current_corridor(self, pos):
        """Returns the corridor that encloses any given pos"""
        tile_pos = pos[0] // TILESIZE, pos[1] // TILESIZE
        for corridor in self._generator_corridors:
            if corridor.get_x() < tile_pos[0] < corridor.get_end_x():
                if corridor.get_y() < tile_pos[1] < corridor.get_end_y():
                    return corridor
        return False

    def get_room_or_corridor(self, pos):
        room = self.get_current_room(pos)
        if room:
            return room
        else:
            return  self.get_current_corridor(pos)

    def get_connected_rooms_corridors(self, pos):
        """Returns the connected rooms and corridors that surround a given pos"""
        room = self.get_current_room(pos)
        if not room:
            corridor = self.get_current_corridor(pos)
            return [*self._adjacent_matrix.get_connected_nodes(corridor)]
        else:
            return self._adjacent_matrix.get_connected_edges(room)

    def is_adjacent(self, room1, room2):
        self._adjacent_matrix.test_adjacent(room1, room2)

    def _load_walls(self, game):
        for rno, row in enumerate(self._map_layout):
            for cno, char in enumerate(row):
                if char == "#":
                    game.walls.add(Wall(game, cno, rno))

    def _load_internals(self, game):
        """Places all enemies, crated and exits in the level"""
        # Following code runs for each individual room in the level
        for room in self._generator_rooms:
            room_area = (room.get_height() - 2) * (room.get_width() - 2)
            # Calculates no. of enemies to add to room based on adaptive difficulty score
            num_enemies = random.randint(0, math.floor((room_area/100)*game.get_comp_diff()*2))
            # Assigns boolean True or False on if crate should be added based on adaptive difficulty score
            add_crate = random.randrange(0, 2) < 1 / game.get_comp_diff()

            # Add's random positions to the list enemy_positions such that all positions within room and unique
            enemy_count = 0
            enemy_positions = []
            while enemy_count < num_enemies:
                pos = self._get_random_pos(room)
                if not pos in enemy_positions:
                    enemy_positions.append(pos)
                    enemy_count += 1

            # Instantiates enemy objects at previously ascertained positions
            for enemy_pos in enemy_positions:
                game.enemies.add(Enemy(game, enemy_pos[0] * TILESIZE, enemy_pos[1] * TILESIZE))

            # Add's crate to a position in room if add_crate was True and position is unoccupied by an enemy
            if add_crate:
                crate_added = False
                while not crate_added:
                    pos = self._get_random_pos(room)
                    if not pos in enemy_positions:
                        game.crates.add(Crate(game, pos[0], pos[1]))
                        crate_added = True

    def _get_random_pos(self, room):
        """Returns a random global position within a given room"""
        rand_pos_offset_x = random.randint(1, room.get_width() - 2)
        rand_pos_offset_y = random.randint(1, room.get_height() - 2)
        rand_pos_x = room.get_x() + rand_pos_offset_x
        rand_pos_y = room.get_y() + rand_pos_offset_y
        return rand_pos_x, rand_pos_y
