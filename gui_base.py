import pygame as pg


class GUI:
    """Template GUI Class used for constructing other GUI element sub-classes"""
    def __init__(self, controller, pos, width, height):
        self.controller = controller
        self._pos = pos
        self._width = width
        self._height = height
        self._visible = True

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_pos(self):
        return self._pos

    def get_visible(self):
        return self._visible

    def set_pos(self, new_pos):
        self._pos = new_pos

    def set_visible(self, boolean):
        self._visible = boolean


class Bar(GUI):
    def __init__(self, controller, pos, width, height, base_colour, overlay_colour):
        super().__init__(controller, pos, width, height)
        self.c_base = base_colour
        self.c_over = overlay_colour
        self.base_rect = pg.Rect(pos, (width, height))
        self.overlay_rect = pg.Rect(pos, (width, height))
        self._overlay_width = width
        self.empty = False

    def set_pos(self, new_pos):
        self._pos = new_pos
        self.base_rect = pg.Rect(new_pos, (self._width, self._height))
        self.overlay_rect = pg.Rect(new_pos, (self._overlay_width, self._height))

    def set_bar_percent(self, scale):
        if scale == 0:
            self.empty = True
        else:
            self._overlay_width = self._width * scale
            self.overlay_rect = pg.Rect(self._pos, (self._overlay_width, self._height))
            self.empty = False

    def draw(self, offset=(0, 0)):
        if self._visible:
            pg.draw.rect(self.controller._gui_surface, self.c_base, self.base_rect.move(offset[0], offset[1]))
            if not self.empty:
                pg.draw.rect(self.controller._gui_surface, self.c_over, self.overlay_rect.move(offset[0], offset[1]))


class InflatableRect(GUI):
    """GUI Element that can be toggled between two given sizes"""
    def __init__(self, controller, pos, width, height, inflate_scale, colour, image=None):
        super().__init__(controller, pos, width, height)
        self.inflated = False
        self._colour = colour
        self._draw_pos = pos
        # Calculate attributes for when inflated
        self._inflated_width = width * inflate_scale
        self._inflated_height = height * inflate_scale
        self._inflated_pos = (
            pos[0] - ((self._inflated_width - width) // 2), pos[1] - ((self._inflated_height - height) // 2))

        self._surface = pg.Surface((self._width, self._height))
        self._inflated_surface = pg.Surface((self._inflated_width, self._inflated_height))
        if image is not None:
            self._image = pg.image.load("sprites/" + image + ".png").convert_alpha()
        else:
            self._image = pg.image.load("sprites/empty.png").convert_alpha()
        self._image = pg.transform.scale(self._image, (self._width, self._height))
        self._inflated_image = pg.transform.scale(self._image, (int(self._inflated_width), int(self._inflated_width)))
        self._surface.fill(colour)
        self._inflated_surface.fill(colour)
        self._surface.blit(self._image, (0, 0))
        self._inflated_surface.blit(self._inflated_image, (0, 0))

        self._draw_surface = self._surface


    def set_inflated(self, boolean):
        self.inflated = boolean
        if self.inflated:
            self._draw_surface = self._inflated_surface
            self._draw_pos = self._inflated_pos
        else:
            self._draw_surface = self._surface
            self._draw_pos = self._pos

    def set_image(self, image):
        self._image = pg.image.load("sprites/" + image + ".png").convert_alpha()
        self._image = pg.transform.scale(self._image, (self._width, self._height))
        self._inflated_image = pg.transform.scale(self._image, (int(self._inflated_width), int(self._inflated_width)))
        self._surface.fill(self._colour)
        self._inflated_surface.fill(self._colour)
        self._surface.blit(self._image, (0, 0))
        self._inflated_surface.blit(self._inflated_image, (0, 0))


    def get_height(self):
        if self.inflated:
            return self._inflated_height
        return self._height

    def get_width(self):
        if self.inflated:
            return self._inflated_width
        return self._width

    def draw(self):
        if self._visible:
            self.controller.get_surface().blit(self._draw_surface, self._draw_pos)

    def set_pos(self, new_pos):
        self._pos = new_pos
        self._inflated_pos = (new_pos[0] - ((self._inflated_width - self._width) // 2),
                              new_pos[1] - ((self._inflated_height - self._height) // 2))
        if self.inflated:
            self._draw_pos = self._inflated_pos
        else:
            self._draw_pos = self._pos


class Label(GUI):
    def __init__(self, controller, pos, width, height, text, bg_colour, text_colour):
        super().__init__(controller, pos, width, height)
        self._text = text
        self._text_colour = text_colour
        self._bg_colour = bg_colour
        self._font_size = height
        self._font = pg.font.Font('freesansbold.ttf', self._font_size)
        self._set_font_size()
        self._text_surface = self._font.render(self._text, True, self._text_colour)

        self._surface = pg.Surface((width, height))
        self._surface.fill(self._bg_colour)
        self._surface.blit(self._text_surface, ((width-self._text_surface.get_rect().w)//2,0))

    def _set_font_size(self):
        while self._font.get_height() > self._height:
            self._font_size -= 1
            self._font = pg.font.Font('freesansbold.ttf', self._font_size)

    def set_text(self, new_text):
        self._text = new_text
        self._text_surface = self._font.render(self._text, True, self._text_colour)
        self._surface.fill(self._bg_colour)
        self._surface.blit(self._text_surface, ((self._width-self._text_surface.get_rect().w)//2, 0))

    def draw(self):
        if self._visible:
            self.controller.get_surface().blit(self._surface, self._pos)


class Button(GUI):
    def __init__(self, controller, pos, width, height, text, bg_colour, text_colour, func):
        super().__init__(controller, pos, width, height)
        self._func = func
        self._label = Label(controller, pos, width, height, text, bg_colour, text_colour)

    def test_click(self, pos):
        pos = tuple(pos)
        if self._pos[0] <= pos[0] <= self._pos[0] + self._width:
            if self._pos[1] <= pos[1] <= self._pos[1] + self._height:
                return True
        else:
            return False

    def get_func(self):
        return self._func

    def set_pos(self, new_pos):
        self._pos = new_pos
        self._label.set_pos(new_pos)

    def set_text(self, text):
        self._label.set_text(text)

    def draw(self):
        if self._visible:
            self._label.draw()


class TextField(GUI):
    def __init__(self, controller, pos, width, height, bg_colour, text_colour):
        super().__init__(controller, pos, width, height)
        self._bg_colour = bg_colour
        self._text_colour = text_colour
        self._text = ""
        self._label = Label(controller, pos, width, height, self._text, bg_colour, text_colour)

        self._active = False

    def test_click(self, pos):
        pos = tuple(pos)
        if self._pos[0] <= pos[0] <= self._pos[0] + self._width:
            if self._pos[1] <= pos[1] <= self._pos[1] + self._height:
                return True
        else:
            return False

    def set_active(self, boolean):
        self._active = boolean

    def get_active(self):
        return self._active

    def set_text(self, new_text):
        self._text = new_text
        self._label.set_text(new_text)

    def get_text(self):
        return self._text

    def update_text(self, new_char):
        if new_char == "~":
            self._text = self._text[:-1]
        else:
            self._text += new_char
        self._label.set_text(self._text)

    def set_pos(self, new_pos):
        self._pos = new_pos
        self._label.set_pos(new_pos)

    def draw(self):
        if self._visible:
            self._label.draw()


class GridLayout:
    """A class for controlling the relative positions of all contained elements in a grid like structure"""
    def __init__(self, pos, rows, columns, padding_x=20, padding_y=20):
        self._pos = pos
        self._rows = rows
        self._columns = columns
        self._visible = True
        self._padding_x = padding_x
        self._padding_y = padding_y
        self._width = 0
        self._height = 0

        # Grid elements are initialised as empty sets of zero/none values
        self._grid_elements = [[None for i in range(columns)] for j in range(rows)]
        # Grid sizes is list of column widths followed by list of row heights (max of each element)
        self._grid_sizes = [[0 for i in range(columns)], [0 for j in range(rows)]]

    def __iter__(self):
        self._iter_pos = 0
        return self

    def __next__(self):
        """Python builtin method that allows grid layout to be iterated over
        Iteration acts from right to left followed by top to bottom of grid"""
        while self._iter_pos < self._rows * self._columns:
            row_num = self._iter_pos // self._columns
            col_num = self._iter_pos % self._columns

            element = self._grid_elements[row_num][col_num]
            self._iter_pos += 1
            if element is not None:
                return element

        raise StopIteration

    def add_element(self, element, pos):
        """Add a GUI element to the grid at the specified position"""
        self._grid_elements[pos[1]][pos[0]] = element
        if element.get_width() > self._grid_sizes[0][pos[0]]:
            self._grid_sizes[0][pos[0]] = element.get_width()
        if element.get_height() > self._grid_sizes[1][pos[1]]:
            self._grid_sizes[1][pos[1]] = element.get_height()

    def _update_sizes(self):
        """Private method that is used to ensure width/height of each column/row is at least equivalent
        to the largest width andr height element within said column/row"""
        # Sets row heights
        for row_num, row in enumerate(self._grid_elements):
            max_h = 0
            for element in row:
                if element is not None:
                    if element.get_height() > max_h:
                        max_h = element.get_height()
            self._grid_sizes[1][row_num] = max_h

        # Sets column widths
        for col_num in range(self._columns):
            max_w = 0
            for row_num in range(self._rows):
                if self._grid_elements[row_num][col_num] is not None:
                    if self._grid_elements[row_num][col_num].get_width() > max_w:
                        max_w = self._grid_elements[row_num][col_num].get_width()
                        self._grid_sizes[0][col_num] = max_w

    def update_elements(self):
        """Call once all elements are added to grid or if additional elements are added
        This method updates positions of all elements in the grid to the correct position"""
        self._update_sizes()
        row_height_total = 0
        # Iterate through the elements in the grid
        for row_num, row in enumerate(self._grid_elements):
            col_width_total = 0
            row_height = self._grid_sizes[1][row_num]
            for col_num, element in enumerate(row):
                col_width = self._grid_sizes[0][col_num]
                # Check if element exists at a given position
                if element is not None:
                    # Check if element is an InflatableRect as calculating offsets is treated differently
                    if type(element) is InflatableRect:
                        if element.inflated:
                            x_offset = ((col_width - element.get_width()) // 2) + (
                                    self._padding_x * col_num // 2) + col_width_total + (
                                               (element._inflated_width - element._width) // 2)
                            y_offset = ((row_height - element.get_height()) // 2) + (
                                    self._padding_y * row_num // 2) + row_height_total + (
                                               (element._inflated_height - element._height) // 2)
                        else:
                            x_offset = ((col_width - element.get_width()) // 2) + (
                                    self._padding_x * col_num // 2) + col_width_total
                            y_offset = ((row_height - element.get_height()) // 2) + (
                                    self._padding_y * row_num // 2) + row_height_total
                    # Otherwise update offsets
                    else:
                        x_offset = ((col_width - element.get_width()) // 2) + (
                                self._padding_x * col_num // 2) + col_width_total
                        y_offset = ((row_height - element.get_height()) // 2) + (
                                self._padding_y * row_num // 2) + row_height_total
                    element.set_pos((self._pos[0] + x_offset, self._pos[1] + y_offset))
                col_width_total += col_width
            row_height_total += row_height

            self._width = col_width_total + (self._padding_x * self._columns)
            self._height = col_width_total + (self._padding_y * self._rows)

    def draw(self):
        for element in self:
            element.draw()

    def get_visible(self):
        return self._visible

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_element(self, pos):
        return self._grid_elements[pos[1]][pos[0]]

    def set_pos(self, pos):
        self._pos = pos
        self.update_elements()
