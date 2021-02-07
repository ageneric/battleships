import pygame as pg
from interface import Button
from defaults import *

class GridSwitchOnce(Button):
    """A single use switch-button for use in a grid."""
    def __init__(self, rect, message, col=None, row=None, callback=None, **kwargs):
        super().__init__(rect, message, callback, **kwargs)
        self.col = col
        self.row = row

    def on_click(self):
        self.enabled = False  # Disables the button.
        self.callback(self.col, self.row)

def layout_grid(x, y, spacing, width=10, height=10):
    for col in range(width):
        for row in range(height):
            yield x + spacing*col, y + spacing*row, col, row

def snap_to_grid(mouse_x, mouse_y, x, y, spacing: int):
    exact_column = (mouse_x - x) // spacing
    exact_row = (mouse_y - y) // spacing

    return exact_column, exact_row

"""def position_in_grid(col, row, x, y, spacing: int):
    return x + spacing * col, y + spacing * row"""

class TrackingBoard:
    """10*10 "tracking" grid for the player to select opponent tiles to reveal."""
    def __init__(self, pos_x, pos_y, callback, arrangement, width=10, height=10):
        self.enabled = True
        self.disable_input = False

        self.tiles = []
        for x, y, col, row in layout_grid(pos_x, pos_y, 32, width, height):
            # When revealed, colour depends on if the opponent tile hides a ship.
            if arrangement[row][col] is not None:
                reveal_color = C_YELLOW  # indicate destroyed ships
            else:
                reveal_color = C_DARK_BLUE  # indicate misses

            button = GridSwitchOnce((x, y, 28, 28), "", col, row, callback,
                                    background=C_LIGHT_ISH, background_disabled=reveal_color)
            self.tiles.append(button)

    def update(self):
        pass

    def draw(self, screen):
        if self.enabled:
            for tile in self.tiles:
                tile.draw(screen)

    def mouse_event(self, event):
        if self.enabled and not self.disable_input:
            for tile in self.tiles:
                tile.mouse_event(event)
