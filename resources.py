import pygame as pg
import os.path

class TileSpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
        except pg.error as e:
            raise SystemExit(f"{e}: {filename}")

    def load_image(self, rect, tile_size=1):
        """Cuts out a rectangle from the loaded sprite sheet."""
        rect = pg.Rect(tuple(dimension * tile_size for dimension in rect))
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        image.set_colorkey((0, 0, 0))
        return image

def load_ship_images():
    """Generates the ship_images dictionary."""
    default_ship_types = {
        "Patrol Boat": 2, "Submarine": 3, "Destroyer": 3,
        "Battleship": 4, "Aircraft Carrier": 5
    }
    ship_sprite_sheet = TileSpriteSheet(os.path.join("Assets", "tile_ships.png"))
    ship_images = {}

    for row, (name, size) in enumerate(default_ship_types.items()):
        ship_images[name] = (
            ship_sprite_sheet.load_image((0, row, size, 1), 16),  # default image
            ship_sprite_sheet.load_image((5, row, size, 1), 16))  # blueprint-style image
    return ship_images

def get_ship_image(ship, ship_images, grid_x, grid_y, spacing: int, palette=0):
    try:
        image = ship_images[ship.name][palette]
        image = pg.transform.scale(image, (spacing * ship.size, spacing))
    except KeyError:
        image = pg.Surface((spacing * ship.size, spacing))

    image = pg.transform.rotate(image, 0 if ship.horizontal else 90)
    x = grid_x + spacing * ship.origin_col
    y = grid_y + spacing * ship.origin_row
    return image, x, y

def load_audio(keys=None):
    """Generates the audio dictionary."""
    paths = {
        "begin": os.path.join("Assets", "ht-ostinato.ogg"),
        "alert": os.path.join("Assets", "ht-interact.ogg"),
        "cue": os.path.join("Assets", "sfx-lowblip.wav"),
        "hit": os.path.join("Assets", "sfx-bitnoise.ogg"),
        "sink": os.path.join("Assets", "sfx-bitflare.ogg")
    }
    if keys is None:
        keys = paths.keys()
    sounds = {}

    for key in keys:
        sounds[key] = pg.mixer.Sound(paths[key])

    return sounds
