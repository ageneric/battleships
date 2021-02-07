from random import randint, choice
import base64

class Ship:
    def __init__(self, origin_col: int, origin_row: int, size: int, horizontal: bool,
                 name=""):
        self.origin_col = origin_col  # leftmost coordinate
        self.origin_row = origin_row  # uppermost coordinate
        self.size = size  # the length of the ship
        self.horizontal = horizontal  # ship orientation
        self.name = name

    def tile_indexes(self):
        """The tile indexes that this ship covers (col, row)."""
        for i in range(self.size):
            if self.horizontal:
                yield self.origin_col + i, self.origin_row
            else:
                yield self.origin_col, self.origin_row + i

    def destroyed(self, revealed) -> bool:
        return all(revealed[row][col] for col, row in self.tile_indexes())

def default_ships():
    return [
        Ship(0, 0, 2, True, "Patrol Boat"),
        Ship(0, 1, 3, True, "Submarine"),
        Ship(0, 2, 3, True, "Destroyer"),
        Ship(0, 3, 4, True, "Battleship"),
        Ship(0, 4, 5, True, "Aircraft Carrier")
    ]


Valid, OutOfBounds, Overlap, OverlapAdjacent = range(4)

def generate_blank_grid(default_value, width=10, height=10):
    return [[default_value for _tile in range(width)] for _row in range(height)]

def check_ship_position(ship, arrangement, width=10, height=10) -> int:
    """Returns an integer 0 <= x <= 2, where 0 -> valid ship position.
    1 -> out of bounds, 2 -> overlapping ship.
    """
    for col, row in ship.tile_indexes():
        # If tile is out of bounds or occupied, the ship is invalid.
        if col < 0 or col >= width or row < 0 or row >= height:
            return OutOfBounds
        elif arrangement[row][col] is not None:
            return Overlap
    return Valid

def remove_ship(ship, ships, arrangement):
    for col, row in ship.tile_indexes():
        arrangement[row][col] = None  # remove reference to deleted or moved ship
    ships.remove(ship)

def place_ship(ship, ships, arrangement):
    for col, row in ship.tile_indexes():
        arrangement[row][col] = ship  # update references to point to the new ship
    ships.append(ship)

def generate_computer_layout(ships, arrangement, stock_ships, width=10, height=10):
    """Randomly generates a valid layout and stores it in ships."""
    assert width > 5 and height > 5  # minimum board size to fit all ships

    for ship in stock_ships:
        # Loop until valid: with default ships, there will always be a valid position.
        placed = False
        while not placed:
            ship.origin_col = randint(0, width)
            ship.origin_row = randint(0, height)
            ship.horizontal = choice((False, True))

            if check_ship_position(ship, arrangement, width, height) == Valid:
                placed = True

        place_ship(ship, ships, arrangement)

def adjacent_tiles(col: int, row: int, width=10, height=10):
    for offset in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        nearby_col = col + offset[0]
        nearby_row = row + offset[1]

        if 0 <= nearby_col < width and 0 <= nearby_row < height:
            yield nearby_col, nearby_row, offset

def encode_layout(ships) -> bytes:
    serialised = []
    for ship in ships:
        serialised.append("-".join(map(str, (ship.origin_col, ship.origin_row, ship.size,
                                             int(ship.horizontal), ship.name))))
    serial_bytes = bytes(",".join(serialised), "utf-8")
    return base64.b64encode(serial_bytes)

def decode_layout(encoded: bytes):
    serial_bytes = base64.b64decode(encoded)
    serialised = serial_bytes.decode("utf-8").split(",")

    for ship_string in serialised:
        s_col, s_row, s_size, s_horizontal, name = ship_string.split("-")
        col, row, size, horizontal = map(int, (s_col, s_row, s_size, s_horizontal))
        horizontal = bool(horizontal)
        yield Ship(col, row, size, horizontal, name)


if __name__ == "__main__":
    # `Test: check_ship_position(ship, arrangement)`
    test_arrangement = generate_blank_grid(None, width=10, height=10)

    test_ship = Ship(4, 0, 2, True)
    for test_col, test_row in test_ship.tile_indexes():
        test_arrangement[test_row][test_col] = test_ship

    assert Valid == check_ship_position(Ship(0, 0, 4, True), test_arrangement)
    assert OutOfBounds == check_ship_position(Ship(0, -1, 2, False), test_arrangement)
    assert OutOfBounds == check_ship_position(Ship(-1, 0, 2, True), test_arrangement)
    assert OutOfBounds == check_ship_position(Ship(3, 0, 20, False), test_arrangement,
                                              width=10, height=10)
    assert Overlap == check_ship_position(Ship(3, 0, 2, True), test_arrangement)
    print("Test passed: check_ship_position()")
