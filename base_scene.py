from defaults import C_BLACK
from interface import MOUSE_EVENTS

class Scene:
    """Each scene manages the screen, updated and drawn
    once per frame. To switch scene, the new scene flag
    is set to the next scene (detect this in main loop).
    """
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.actors = []

        self.mouse_handlers = []

        self.flag_new_scene = None
        self.flag_new_scene_args = []

    def update(self):
        for actor in self.actors:
            actor.update()

    def draw(self):
        self.screen.fill(C_BLACK)
        for actor in self.actors:
            actor.draw(self.screen)

    def handle_events(self, pygame_events):
        for event in pygame_events:
            if event.type in MOUSE_EVENTS:
                for button in self.mouse_handlers:
                    button.mouse_event(event)

    def change_scene(self, new_scene, *args, **kwargs):
        self.flag_new_scene = new_scene
        self.flag_new_scene_args = args
        self.flag_new_scene_kwargs = kwargs

    # Utility functions
    def add_mouse_handler(self, interactable):
        self.mouse_handlers.append(interactable)
        self.actors.append(interactable)

    def display_width(self) -> int:
        return self.screen.get_size()[0]

    def display_height(self) -> int:
        return self.screen.get_size()[1]
