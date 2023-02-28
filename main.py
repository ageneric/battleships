"""A graphical solution to Battleships! by Kevin Gao"""

# pygame 1.9.6 (Python 3.8.2)
import pygame as pg
from scenes import ChooseMode
from defaults import *

print('1/3 Starting: pygame initialisation')
FPS = 60
clock = pg.time.Clock()

pg.init()

def main():
    print(f'2/3 Starting: screen resolution {display_width}, {display_height}.')
    screen = pg.display.set_mode((display_width, display_height))
    pg.mixer.pre_init(22050, -16, 2, 512)

    print('3/3 Starting: main loop')
    scene = ChooseMode(screen, clock)

    running = True

    while running:
        # Handle events --- (pg.key.get_pressed() for pressed keys)
        if pg.event.get(pg.QUIT):
            running = False
        else:
            scene.handle_events(pg.event.get())

        # Scene switching ---
        if scene.flag_new_scene is not None:
            scene = scene.flag_new_scene(screen, clock, *scene.flag_new_scene_args,
                                         **scene.flag_new_scene_kwargs)

        # Update scene and display --
        scene.update()
        if clock.get_rawtime() < 1000 / FPS:
            scene.draw()

        pg.display.flip()

        clock.tick(FPS)


if __name__ == "__main__":
    main()

pg.quit()
