from random import choice
from battleships import generate_blank_grid

class OpportunityPlayer:
    """Bad idea - find the position on the grid which
    matches the most possible ship placements and fire at it."""
    def __init__(self, ships, arrangement, revealed, width=10, height=10):
        self.ships = ships
        self.arrangement = arrangement
        self.revealed = revealed
        self.width = width
        self.height = height

        self.priority = generate_blank_grid(0, width, height)

    def play_move(self):
        if all(all(tile for tile in row) for row in self.revealed):
            return None, None  # all tiles have been revealed

        self.priority = generate_blank_grid(0, self.width, self.height)

        for col, row in self.revealed_grid_tiles():
            if (self.arrangement[row][col] is not None
                    and not self.arrangement[row][col].destroyed(self.revealed)):
                self.fit_ships_around(col, row)

        # Overwrite the priority of already revealed tiles with -1.
        for col, row in self.revealed_grid_tiles():
            self.priority[row][col] = -1

        highest = max(max(row for row in col) for col in self.priority)

        if highest == -1:  # if all tiles are revealed, give up.
            return None, None
        # From all moves that are equally highest priority, randomly
        # choose a move (if no exposed ships, this is effectively random fire).
        options = []
        for col in range(self.width):
            for row in range(self.height):
                if self.priority[row][col] == highest:
                    options.append((col, row))
        return choice(options)

    def revealed_grid_tiles(self):
        """Generator that yields the coordinates of all revealed tiles."""
        for col in range(self.width):
            for row in range(self.height):
                if self.revealed[row][col]:
                    yield col, row

    def fit_ships_around(self, col: int, row: int):
        """Consider all possible ship placements around the tile
        and increase the weight of tiles which hide ships in many arrangements."""
        for ship in self.ships:
            if ship.destroyed(self.revealed):
                continue

            # Horizontal placements:
            minimum_col = max(0, col - ship.size + 1)
            ships_to_fit = min(ship.size, self.width - col)

            for offset in range(ships_to_fit):
                start = minimum_col + offset
                ship_tiles = [tile_col for tile_col in range(start, start + ship.size)]

                # Placement is only considered if it doesn't overlap a revealed empty tile.
                if all(not self.revealed[row][tile_col] or self.arrangement[row][tile_col]
                       for tile_col in ship_tiles):
                    for tile_col in ship_tiles:
                        self.priority[row][tile_col] += 1

            # Vertical placements:
            minimum_row = max(0, row - ship.size + 1)
            ships_to_fit = min(ship.size, self.height - row)

            for offset in range(ships_to_fit):
                start = minimum_row + offset
                ship_tiles = [tile_row for tile_row in range(start, start + ship.size)]

                # Placement is only considered if it doesn't overlap a revealed empty tile.
                if all(not self.revealed[tile_row][col] or self.arrangement[tile_row][col]
                       for tile_row in ship_tiles):
                    for tile_row in ship_tiles:
                        self.priority[tile_row][col] += 1
