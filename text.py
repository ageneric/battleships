import pygame as pg
from typing import Union

pg.font.init()
main_font = pg.font.SysFont('Calibri', 16)

COLOR_DEFAULT = (191, 131, 191)
BACKGROUND_DEFAULT = (15, 15, 15)
BOX_PADDING = 5

_sprite_cache = {}

def draw(surface, message: str, position, font=main_font, color=COLOR_DEFAULT,
         text_sprite=None, static=False, justify: Union[bool, list, tuple] = False):
    """Draws text to the surface at the (x, y) position specified.
    Justify - set to True/False to centre in both axes, or
              pick each of the (x, y) axes to justify with, i.e.
              (True, False) centres horizontally & not vertically.
    Static - cache this text's sprite - for faster drawing.
    """
    if text_sprite is None:
        text_sprite = render(message, font, color, static)

    x, y = position
    if justify:
        text_rect = text_sprite.get_rect()
        if justify is True or justify[0] is True:
            x -= text_rect.width / 2
        if justify is True or justify[1] is True:
            y -= text_rect.height / 2

    return surface.blit(text_sprite, (x, y))

def render(message, font=main_font, color=COLOR_DEFAULT, save_sprite=True):
    """Render text, using the sprite cache if possible.
    Adds to sprite cache when called directly / rendering static text.
    """
    text_sprite = _sprite_cache.get((message, font, *color))

    if text_sprite is None:
        text_sprite = font.render(message, True, color)
        if save_sprite:
            _sprite_cache[(message, font, *color)] = text_sprite

    return text_sprite

def box(surface, message: str, position, width=None, height=None, middle=False,
        box_color=BACKGROUND_DEFAULT, font=main_font, color=COLOR_DEFAULT):
    """Blits a text box to the surface at position, a pair
    of (x, y) coordinates. Width and height, if omitted, fit
    the text's size (with padding). Middle centres text.
    """
    if width is None or height is None:
        text_sprite = render(message, font, color, save_sprite=True)
        if width is None:
            width = text_sprite.get_rect().width + 2*BOX_PADDING
        if height is None:
            height = text_sprite.get_rect().height + 2*BOX_PADDING

    box_rect = pg.Rect(position, (width, height))
    pg.draw.rect(surface, box_color, box_rect)

    if message:
        if middle:
            draw(surface, message, box_rect.center, font, color, justify=True)
        else:
            draw(surface, message, (position[0] + BOX_PADDING, box_rect.centery),
                 font, color, justify=(False, True))

    return box_rect
