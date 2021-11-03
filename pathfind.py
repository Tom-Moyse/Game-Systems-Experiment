class Stack:
    """Basic implementation of a stack data structure (works as a wrapper for a list)"""
    def __init__(self, data: list):
        self._data = data

    def pop(self):
        return self._data.pop()

    def push(self, item):
        self._data.append(item)

    def length(self):
        return len(self._data)


class _Square:
    """Basic data structure utilised in calculating the optimum route within pathfinder class"""
    def __init__(self, x, y, target, parent):
        self._x = x
        self._y = y
        self.target = target
        self.parent = parent
        self._g_score = self.compute_g_score()
        self._h_score = self.compute_h_score()
        self._f_score = self.compute_f_score()

    def is_root(self):
        return False

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_f_score(self):
        return self._f_score

    def get_g_score(self):
        return self._g_score

    def compute_g_score(self):
        return self.parent.get_g_score() + 1

    def compute_h_score(self):
        return self.calculate_distance((self._x,self._y), self.target)

    def compute_f_score(self):
        return self._g_score + self._h_score

    def calculate_distance(self,pos1,pos2):
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])


class _RootSquare(_Square):
    """Specific route tile: doesn't have a parent tile"""
    def __init__(self, x, y, target):
        self._x = x
        self._y = y
        self.target = target
        self._g_score = 0
        self._h_score = self.calculate_distance((x,y), target)
        self._f_score = self._h_score

    def is_root(self):
        return True


class Pathfinder():
    def __init__(self, start_pos, end_pos, map_data):
        self._start_pos = start_pos
        self._end_pos = end_pos
        self._map_data = map_data

        # Initialise start point for pathfinding
        self._source_square = _RootSquare(self._start_pos[0], self._start_pos[1], self._end_pos)
        self._open_list = [self._source_square]
        self._closed_list = []

        self.valid_path = self._find_path()

    def _find_path(self):
        """Implementation of A* pathfinding algorithm"""
        # Loop runs until a path is found or all possible options exhausted
        while len(self._open_list) != 0:
            # Grabs square with lowest f score from the open list and moves to closed list
            current_square = self._lowestFScore()
            self._closed_list.append(current_square)
            self._open_list.remove(current_square)

            # Checks if end point of search has been reached
            for square in self._closed_list:
                if square.get_x() == self._end_pos[0] and square.get_y() == self._end_pos[1]:
                    return True

            # Grabs all squares adjacent to one currently inspected
            adjacentSquares = self._get_adjacent_squares(current_square)
            for aSquare in adjacentSquares:
                # Checks if square has already been inspected
                if self._check_similar_square(aSquare, self._closed_list):
                    continue
                # Adds square to open list if not already within open list
                if not self._check_similar_square(aSquare, self._open_list):
                    self._open_list.append(aSquare)
                # If in open list already checks if more efficient path to this square has been identified
                # and sets squares 'parent' as appropriate
                else:
                    if current_square.get_g_score() < aSquare.get_g_score():
                        aSquare.parent = current_square
        # Only reached if finding path was impossible and thus unsuccessful
        return False



    def _check_similar_square(self, aSquare, aList):
        """Check if square in same position already exists within given list"""
        pos_x = aSquare.get_x()
        pos_y = aSquare.get_y()
        for square in aList:
            if pos_x == square.get_x() and pos_y == square.get_y():
                return True
        return False

    def _get_adjacent_squares(self, current_square):
        """Returns all squares that are adjacent N/E/S/W from current position"""
        adjacents = []
        offsets = ((1,0),(0,-1),(-1,0),(0,1))
        for offset in offsets:
            x_pos = int(current_square.get_x()) + offset[0]
            y_pos = int(current_square.get_y()) + offset[1]
            tile = self._map_data[y_pos][x_pos]
            if tile != "#":
                adjacents.append(_Square(x_pos, y_pos, self._end_pos, current_square))
        return adjacents

    def _lowestFScore(self):
        """Returns square in open list with the lowest f score"""
        lowest_f_score = -1
        lowest_square = None
        for square in self._open_list:
            if (lowest_f_score == -1) or square.get_f_score() < lowest_f_score:
                lowest_f_score = square.get_f_score()
                lowest_square = square
        return lowest_square

    def is_valid_path(self):
        # Interface to check if a valid path was found
        return self.valid_path

    def get_shortest_route(self):
        # Interface to allow the shortest route identified to be returned as a stack of squares
        # In order that the enemy should traverse to reach target destination
        orderedSquareRoute = []
        square = self._closed_list[-1]
        while not square.is_root():
            orderedSquareRoute.append(square)
            square = square.parent

        route = []
        for square in orderedSquareRoute:
            route.append((square.get_x(), square.get_y()))

        return Stack(route)
