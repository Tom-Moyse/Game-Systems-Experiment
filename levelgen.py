import random


class _Node:
    """Subclass used as part of LevelTree data structure"""
    def __init__(self, parent, data):
        self._data = data

        self._left_node = None
        self._right_node = None
        self._parent = parent

    def set_left_node(self, node):
        self._left_node = node

    def set_right_node(self, node):
        self._right_node = node

    def get_left_node(self):
        return self._left_node

    def get_right_node(self):
        return self._right_node

    def get_data(self):
        return self._data

    def set_data(self, new_data):
        self._data = new_data


class LevelTree:
    """A Binary tree data structure that is used to represent a level within the game
    The top node in the tree represents the entire level region with sub-nodes representing
    their own respective sub-regions"""
    def __init__(self, num_rows, num_columns):
        region = Region(0, (0, 0), num_columns, num_rows)
        self._source_node = _Node(self, region)

    def get_nodes_at_depth(self, depth):
        """Return's all nodes at a given 'depth' within the tree via traversing all nodes within the tree"""
        check_list = [self._source_node]
        depth_nodes = []

        while len(check_list) != 0:
            current_node = check_list[0]
            check_list.remove(current_node)
            if current_node.get_data().get_depth() == depth:
                depth_nodes.append(current_node)
            else:
                check_list.append(current_node.get_left_node())
                check_list.append(current_node.get_right_node())

        return depth_nodes

    def get_source_node(self):
        return self._source_node


class Region:
    def __init__(self, depth, pos, width, height):
        self._depth = depth

        self._pos = pos
        self._width = width
        self._height = height
        self._end_pos = (self._pos[0] + width - 1, self._pos[1] + height - 1)

        self._left_rooms = []
        self._right_rooms = []
        self._corridors = []

    def add_left_room(self, new_room):
        self._left_rooms.append(new_room)

    def add_right_room(self, new_room):
        self._right_rooms.append(new_room)

    def add_corridor(self, new_corridor):
        self._corridors.append(new_corridor)

    def get_left_rooms(self):
        return self._left_rooms

    def get_right_rooms(self):
        return self._right_rooms

    def get_corridors(self):
        return self._corridors

    def get_depth(self):
        return self._depth

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_pos(self):
        return self._pos

    def get_x(self):
        return self._pos[0]

    def get_y(self):
        return self._pos[1]

    def get_end_pos(self):
        return self._end_pos


class Room:
    def __init__(self, parent_region, width, height, relative_pos=None, absolute_pos=None):
        self._parent_region = parent_region
        self._width = width
        self._height = height

        if absolute_pos is None:
            self._relative_pos = relative_pos
            self._pos = (parent_region.get_x() + relative_pos[0], parent_region.get_y() + relative_pos[1])
        else:
            self._pos = absolute_pos
            self._relative_pos = (absolute_pos[0] - parent_region.get_x(), absolute_pos[1] - parent_region.get_y())

        self._end_pos = self._pos[0] + self._width - 1, self._pos[1] + self._height - 1

    def get_rel_pos(self):
        return self._relative_pos

    def get_rel_x(self):
        return self._relative_pos[0]

    def get_rel_y(self):
        return self._relative_pos[1]

    def get_pos(self):
        return self._pos

    def get_x(self):
        return self._pos[0]

    def get_y(self):
        return self._pos[1]

    def get_end_pos(self):
        return self._end_pos

    def get_end_x(self):
        return self._end_pos[0]

    def get_end_y(self):
        return self._end_pos[1]

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height


class Corridor(Room):
    def __init__(self, parent_region, width, height, left_room, right_room, direction, relative_pos=None, absolute_pos=None):
        super().__init__(parent_region, width, height, relative_pos, absolute_pos)
        self._left_room = left_room
        self._right_room = right_room
        self._direction = direction

    def get_left_room(self):
        return self._left_room

    def get_right_room(self):
        return self._right_room

    def get_direction(self):
        return self._direction

    def set_x(self, new_x):
        self._pos = (new_x, self._pos[1])

    def set_y(self, new_y):
        self._pos = (self._pos[0], new_y)

    def set_end_x(self, new_x):
        self._end_pos = (new_x, self._end_pos[1])

    def set_end_y(self, new_y):
        self._end_pos = (self._end_pos[0], new_y)

    def set_width(self, new_width):
        self._width = new_width

    def set_height(self, new_height):
        self._height = new_height


class LevelGenerator:
    """Class used to generate levels for the game based on small number of parameters"""
    def __init__(self, num_columns, num_rows, recurse_depth, split_deviation):
        self._level_layout = [[" " for i in range(num_columns)] for j in range(num_rows)]
        self._level_tree = LevelTree(num_rows, num_columns)
        self._max_recurse_depth = recurse_depth
        self._split_deviation = split_deviation

        # Splits level into regions and appends these regions to level trees' nodes data attributes
        self._recursive_split(self._level_tree.get_source_node())

        # Place room (data for room) in level trees node data
        self._gen_rooms()

        # In unlikely event that not all rooms can be linked 'reset' method is called
        if not self._gen_corridors():
            self._reset(num_columns, num_rows)
            return
        # Otherwise generate the level map based on the newly created level tree
        else:
            self._gen_map_from_tree()
            self._main_region = self._level_tree.get_source_node().get_data()

    def get_rooms(self):
        return [*self._main_region.get_left_rooms(), *self._main_region.get_right_rooms()]

    def get_corridors(self):
        return self._main_region.get_corridors()

    def get_layout(self):
        return self._level_layout

    def _reset(self, num_columns, num_rows):
        """Method performs required parts of the 'init' method to re-initialised the class"""
        self._level_layout = [[" " for i in range(num_columns)] for j in range(num_rows)]
        self._level_tree = LevelTree(num_rows, num_columns)
        self._recursive_split(self._level_tree.get_source_node())
        self._gen_rooms()
        if not self._gen_corridors():
            self._reset(num_columns, num_rows)
            return
        else:
            self._gen_map_from_tree()
            self._main_region = self._level_tree.get_source_node().get_data()

    def _gen_map_from_tree(self):
        node = self._level_tree.get_source_node()
        region = node.get_data()
        left_rooms = region.get_left_rooms()
        right_rooms = region.get_right_rooms()
        corridors = region.get_corridors()

        # Places room wall tiles in the level layout 2d array
        for room in left_rooms:
            # Place horizontal room tiles
            for room_x in range(room.get_width()):
                self._level_layout[room.get_pos()[1]][room.get_pos()[0] + room_x] = "#"
                self._level_layout[room.get_pos()[1] + room.get_height()-1][room.get_pos()[0] + room_x] = "#"
            # Place vertical room tiles
            for room_y in range(room.get_height()):
                self._level_layout[room.get_pos()[1] + room_y][room.get_pos()[0]] = "#"
                self._level_layout[room.get_pos()[1] + room_y][room.get_pos()[0] + room.get_width()-1] = "#"
        for room in right_rooms:
            # Place horizontal room tiles
            for room_x in range(room.get_width()):
                self._level_layout[room.get_pos()[1]][room.get_pos()[0] + room_x] = "#"
                self._level_layout[room.get_pos()[1] + room.get_height()-1][room.get_pos()[0] + room_x] = "#"
            # Place vertical room tiles
            for room_y in range(room.get_height()):
                self._level_layout[room.get_pos()[1] + room_y][room.get_pos()[0]] = "#"
                self._level_layout[room.get_pos()[1] + room_y][room.get_pos()[0] + room.get_width()-1] = "#"

        # Places corridors wall tiles in level layout
        for corridor in corridors:
            # Place horizontal corridor wall tiles
            for corridor_x in range(corridor.get_width()):
                if corridor_x == 0 or corridor_x == corridor.get_width()-1:
                    self._level_layout[corridor.get_y()][corridor.get_x() + corridor_x] = "#"
                    self._level_layout[corridor.get_end_y()][corridor.get_x() + corridor_x] = "#"
                else:
                    # If not at start or end of corridor then corridor tiles will flip the state of
                    # tiles currently in the level layout, this means that where the corridor and room
                    # intersects an entrance between the two will be formed
                    if self._level_layout[corridor.get_y()][corridor.get_x() + corridor_x] == "#":
                        self._level_layout[corridor.get_y()][corridor.get_x() + corridor_x] = " "
                    else:
                        self._level_layout[corridor.get_y()][corridor.get_x() + corridor_x] = "#"
                    if self._level_layout[corridor.get_end_y()][corridor.get_x() + corridor_x] == "#":
                        self._level_layout[corridor.get_end_y()][corridor.get_x() + corridor_x] = " "
                    else:
                        self._level_layout[corridor.get_end_y()][corridor.get_x() + corridor_x] = "#"
            # Place vertical corridor wall tiles
            for corridor_y in range(corridor.get_height()):
                if corridor_y == 0 or corridor_y == corridor.get_height()-1:
                    self._level_layout[corridor.get_y() + corridor_y][corridor.get_x()] = "#"
                    self._level_layout[corridor.get_y() + corridor_y][corridor.get_end_x()] = "#"
                else:
                    # Functions in the same way as horizontal corridor tile placement
                    if self._level_layout[corridor.get_y() + corridor_y][corridor.get_x()] == "#":
                        self._level_layout[corridor.get_y() + corridor_y][corridor.get_x()] = " "
                    else:
                        self._level_layout[corridor.get_y() + corridor_y][corridor.get_x()] = "#"
                    if self._level_layout[corridor.get_y() + corridor_y][corridor.get_end_x()] == "#":
                        self._level_layout[corridor.get_y() + corridor_y][corridor.get_end_x()] = " "
                    else:
                        self._level_layout[corridor.get_y() + corridor_y][corridor.get_end_x()] = "#"

    def _test_valid_reg(self, width, height, num_splits):
        """Checks if current region will produce an unusable end result for the level layout"""
        # For x remaining splits given room of size A x B can 2^x rooms be formed (of min size 5x5)?
        # Let p + q = x as such A / 2^p >= 5 AND B / 2^q >= 5
        # If solution where positive integers (zero-inclusive) p and q exist then valid split otherwise invalid
        for p in range(num_splits + 1):
            q = num_splits - p
            if width / (2 ** p) >= 5 and height / (2 ** q) >= 5:
                return True
        return False

    def _recursive_split(self, node):
        """Recursively splits the level into sub-regions up until the given recurse depth parameter
        Whilst ensuring that any given region will be valid and continue to be splittable"""
        region = node.get_data()

        if region.get_depth() == self._max_recurse_depth:
            return

        # Randomly selects if split should be horizontal or vertical
        dir = random.randint(0, 1)
        valid_split = False
        splits_remaining = self._max_recurse_depth - region.get_depth()
        cur_width = region.get_width()
        cur_height = region.get_height()


        while not valid_split:
            # Horizontal Split
            if dir == 0:
                # Calculates the point at which to split the region
                split_point = round(
                    cur_width / 2 + cur_width * random.uniform(-self._split_deviation, self._split_deviation))
                # Calculates width of left and right regions
                left_width = split_point
                right_width = cur_width - split_point

                # Checks if both the left and right region would be valid
                if self._test_valid_reg(left_width, cur_height, splits_remaining) and \
                        self._test_valid_reg(right_width, cur_height, splits_remaining):
                    # Instantiate new region objects
                    left_region = Region(region.get_depth() + 1, region.get_pos(), left_width, cur_height)
                    right_region = Region(region.get_depth() + 1,
                                          (region.get_x() + split_point, region.get_y()), right_width, cur_height)
                    # Instantiate new nodes for the level tree and assign them to left and right node variables
                    left_node = _Node(node, left_region)
                    right_node = _Node(node, right_region)
                    valid_split = True

            # Vertical Split
            else:
                # Calculates the point at which to split the region
                split_point = round(
                    cur_height / 2 + cur_height * random.uniform(-self._split_deviation, self._split_deviation))
                # Calculates height of top and bottom regions
                top_height = split_point
                bottom_height = cur_height - split_point

                # Checks if both the top and bottom region would be valid
                if self._test_valid_reg(cur_width, top_height, splits_remaining) and \
                        self._test_valid_reg(cur_width, bottom_height, splits_remaining):
                    # Instantiate new region objects
                    top_region = Region(region.get_depth() + 1, region.get_pos(), cur_width, top_height)
                    bottom_region = Region(region.get_depth() + 1,
                                           (region.get_x(), region.get_y() + split_point), cur_width, bottom_height)
                    # Instantiate new nodes for the level tree and assign them to left and right node variables
                    left_node = _Node(node, top_region)
                    right_node = _Node(node, bottom_region)
                    valid_split = True

            # Re-attempt to split the region by re-selecting randomly the split direction
            dir = random.randint(0, 1)

        # Set the left and right nodes (regions) of the level trees currently inspected parent node (region)
        node.set_left_node(left_node)
        node.set_right_node(right_node)

        # Recursively call the function on the newly instantiated nodes
        self._recursive_split(left_node)
        self._recursive_split(right_node)

    def _gen_rooms(self):
        """Randomly generates room objects that fit within the given regions"""
        base_nodes = self._level_tree.get_nodes_at_depth(self._max_recurse_depth)
        for node in base_nodes:
            region = node.get_data()
            min_w = 5
            min_h = 5
            if round(0.3 * region.get_width()) > min_w:
                min_w = round(0.3 * region.get_width())
            if round(0.3 * region.get_height()) > min_h:
                min_h = round(0.3 * region.get_height())

            room_w = random.randint(min_w, region.get_width())
            room_h = random.randint(min_h, region.get_height())
            room_pos_x = random.randint(0, region.get_width() - room_w)
            room_pos_y = random.randint(0, region.get_height() - room_h)

            new_room = Room(region, room_w, room_h, relative_pos=(room_pos_x, room_pos_y))

            region.add_left_room(new_room)

    def _gen_corridors(self):
        """Wrapper method for the creation of corridor objects to link all given rooms together"""
        for depth in range(self._max_recurse_depth - 1, -1, -1):
            depth_nodes = self._level_tree.get_nodes_at_depth(depth)
            if not self._construct_corridors(depth_nodes):
                return False
        return True

    def _construct_corridors(self, nodes):
        """Generates corridors between all pairs of input rooms"""
        """Returns true/false depending on whether all corridors could be generated or not"""
        for node in nodes:
            regionL = node.get_left_node().get_data()
            regionR = node.get_right_node().get_data()
            main_region = node.get_data()

            for room in regionL.get_left_rooms():
                main_region.add_left_room(room)
            for room in regionL.get_right_rooms():
                main_region.add_left_room(room)
            for corridor in regionL.get_corridors():
                main_region.add_corridor(corridor)

            for room in regionR.get_left_rooms():
                main_region.add_right_room(room)
            for room in regionR.get_right_rooms():
                main_region.add_right_room(room)
            for corridor in regionR.get_corridors():
                main_region.add_corridor(corridor)


            if regionL.get_x() == regionR.get_x():
                # Vertical split occurred (left node is top and right node is bottom region)
                top_rooms = main_region.get_left_rooms()
                bottom_rooms = main_region.get_right_rooms()

                # Select two rooms to link - Highest and lowest respective
                top_room = top_rooms[0]
                for room in top_rooms:
                    if room.get_end_y() > top_room.get_end_y():
                        top_room = room
                bottom_room = bottom_rooms[0]
                for room in bottom_rooms:
                    if room.get_y() < bottom_room.get_y():
                        bottom_room = room

                # Classify rooms by biggest
                big_room = top_room
                small_room = bottom_room
                if small_room.get_width() > big_room.get_width():
                    big_room = bottom_room
                    small_room = top_room

                # Classify rooms by left and right most
                left_room = top_room
                right_room = bottom_room
                if left_room.get_x() > right_room.get_x():
                    left_room = bottom_room
                    right_room = top_room

                if big_room.get_x() <= small_room.get_x() and big_room.get_end_x() >= small_room.get_end_x():
                    # Inclusion overlap
                    x_offset = random.randint(0, small_room.get_width() - 4)
                    x_pos = small_room.get_x() + x_offset
                    y_pos = top_room.get_end_y()
                    corridor = Corridor(main_region, 4, bottom_room.get_y() - y_pos + 1, left_room, right_room,
                                        "V", absolute_pos=(x_pos, y_pos))

                elif left_room.get_end_x() - right_room.get_x() >= 3:
                    # Straight overlap
                    x_offset = random.randint(0, left_room.get_end_x() - right_room.get_x() - 3)
                    x_pos = right_room.get_x() + x_offset
                    y_pos = top_room.get_end_y()
                    corridor = Corridor(main_region, 4, bottom_room.get_y() - y_pos + 1, left_room, right_room,
                                        "V", absolute_pos=(x_pos, y_pos))

                else:
                    corridor = None

            else:
                # Horizontal split
                left_rooms = main_region.get_left_rooms()
                right_rooms = main_region.get_right_rooms()

                # Select two rooms to link (right-most and left-most respectively)
                left_room = left_rooms[0]
                for room in left_rooms:
                    if room.get_end_x() > left_room.get_end_x():
                        left_room = room
                right_room = right_rooms[0]
                for room in right_rooms:
                    if room.get_x() < right_room.get_x():
                        right_room = room

                # Classify rooms by biggest
                big_room = left_room
                small_room = right_room
                if small_room.get_height() > big_room.get_height():
                    big_room = right_room
                    small_room = left_room

                # Classify rooms by top and bottom most
                top_room = left_room
                bottom_room = right_room
                if bottom_room.get_y() < top_room.get_y():
                    top_room = right_room
                    bottom_room = left_room

                if big_room.get_y() <= small_room.get_y() and big_room.get_end_y() >= small_room.get_end_y():
                    # Inclusion overlap
                    y_offset = random.randint(0, small_room.get_height() - 4)
                    y_pos = small_room.get_y() + y_offset
                    x_pos = left_room.get_end_x()
                    corridor = Corridor(main_region, right_room.get_x() - x_pos + 1, 4, left_room, right_room,
                                        "H", absolute_pos=(x_pos, y_pos))

                elif top_room.get_end_y() - bottom_room.get_y() >= 3:
                    y_offset = random.randint(0, top_room.get_end_y() - bottom_room.get_y() - 3)
                    y_pos = bottom_room.get_y() + y_offset
                    x_pos = left_room.get_end_x()
                    corridor = Corridor(main_region, right_room.get_x() - x_pos + 1, 4, left_room, right_room,
                                        "H", absolute_pos=(x_pos, y_pos))

                else:
                    corridor = None

            if corridor is None:
                return False
            else:
                main_region.add_corridor(corridor)

        return True
