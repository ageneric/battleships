import pygame as pg

from interface import Button, Toggle
import text
from base_scene import Scene
from defaults import *
from battleships import default_ships, generate_blank_grid, check_ship_position, \
    generate_computer_layout, encode_layout, decode_layout, place_ship, remove_ship
from components import TrackingBoard, layout_grid, snap_to_grid
from resources import load_ship_images, get_ship_image, load_audio
from computer_player import OpportunityPlayer

ModeSingle, ModeComputer, ModeTwoPlayer = range(3)

class ChooseMode(Scene):
    def __init__(self, screen, clock):
        super().__init__(screen, clock)
        pg.display.set_caption("Battleships! > Select Mode")

        play_mode_0 = Button((180, 55, 280, 33), "Versus Computer", self.mode_computer,
                             color=C_DARK, background=C_LIGHT)
        play_mode_1 = Button((180, 95, 280, 33), "Two Player Local", self.mode_two_player,
                             color=C_DARK, background=C_LIGHT)
        play_mode_2 = Button((180, 135, 280, 33), "Single Board", self.mode_single,
                             color=C_LIGHT, background=C_BLUEPRINT_BLUE)
        quit_button = Button((180, 250, 280, 28), "Quit", cause_quit_event, color=C_RED)

        for button in play_mode_0, play_mode_1, play_mode_2, quit_button:
            self.add_mouse_handler(button)  # buttons register draw, update, mouse events

    def draw(self):
        super().draw()
        text.draw(self.screen, "Battleships! - (git build)", (180, 30),
                  color=C_DARK_ISH)

    def mode_single(self):
        self.change_scene(Setup, ModeSingle)

    def mode_computer(self):
        self.change_scene(Setup, ModeComputer)

    def mode_two_player(self):
        self.change_scene(Setup, ModeTwoPlayer)

class Setup(Scene):
    def __init__(self, screen, clock, mode, player_ships=None, player_arrangement=None, mute=False):
        super().__init__(screen, clock)
        pg.display.set_caption("Battleships! > Designer")

        self.ship_images = load_ship_images()
        self.audio = load_audio(("cue", "alert"))
        self.sound_toggle(mute)  # set sound to muted based on previous setting

        self.mode = mode
        if player_ships is None:
            # New game - use blank board arrangement.
            self.p_stock_ships = (default_ships(), default_ships())
            self.p_arrangement = (generate_blank_grid(None), generate_blank_grid(None))
            self.p_ships = ([], [])
        elif mode == ModeComputer:
            # Rematch game - keep player's placements, re-randomise computer's.
            self.p_stock_ships = ([], default_ships())
            self.p_arrangement = (player_arrangement[0], generate_blank_grid(None))
            self.p_ships = (player_ships[0], [])
        else:
            # Rematch game - keep previous ship placements.
            self.p_stock_ships = ([], [])
            self.p_arrangement = player_arrangement
            self.p_ships = player_ships

        self.turn = 0  # 0 for player 1, 1 for player 2
        self.held_ship = None
        self.mouse_x, self.mouse_y = 0, 0

        # Create buttons and mouse interaction triggers.
        self.start_button = Button(
            (display_width - 145, 242, 145, 28), "Confirm", self.confirm_layout,
            color=C_DARK_BLUE, background=C_LIGHT)
        self.pick_ship_trigger = Button(
            (0, 0, 88, display_height), "", self.pick_ship, background=C_BLUEPRINT_BLUE)
        self.touch_grid_trigger = Button((130, 50, 316, 316), "", self.touch_grid)
        self.touch_grid_trigger.visible = False

        for button in self.start_button, self.pick_ship_trigger, self.touch_grid_trigger:
            self.add_mouse_handler(button)

        # Create sidebar buttons.
        align_right = display_width - 120

        self.export_button = Button(
            (align_right, 50, 120, 28), "Export Layout", self.export_layout,
            color=C_DARK_BLUE, background=C_LIGHT)
        self.import_button = Button(
            (align_right, 80, 120, 28), "Import Layout", self.import_layout,
            color=C_RED, background=C_LIGHT)
        sound_button = Toggle(
            (align_right, 130, 120, 28), "Toggle Sound", self.sound_toggle,
            color=C_DARK_BLUE, background=C_LIGHT)
        sound_button.checked = mute
        back_button = Button(
            (align_right, 180, 120, 28), "Back to Menu", self.change_scene_menu,
            color=C_RED, background=C_LIGHT)

        for button in self.export_button, self.import_button, sound_button, back_button:
            self.add_mouse_handler(button)

    def handle_events(self, pygame_events):
        super().handle_events(pygame_events)

        for event in pygame_events:
            if event.type == pg.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_r and self.held_ship is not None:
                    self.held_ship.horizontal = not self.held_ship.horizontal
                elif event.key == pg.K_ESCAPE:
                    self.return_ship()

    def update(self):
        super().update()

        # Only enable the start button when there are no more ships to place.
        if len(self.p_stock_ships[self.turn]) == 0 and self.held_ship is None:
            self.start_button.enabled = self.start_button.visible = True
            self.export_button.enabled = True
        else:
            self.start_button.enabled = self.start_button.visible = False
            self.export_button.enabled = False

    def draw(self):
        self.screen.fill(C_BLUEPRINT_BLUE)
        for actor in self.actors:
            actor.draw(self.screen)

        # Draw 10*10 grid for alignment.
        for x, y, col, row in layout_grid(130, 50, 32):
            pg.draw.rect(self.screen, C_HIGHLIGHT_BLUE, (x, y, 28, 28))

        # Draw the placed ships.
        for ship in self.p_ships[self.turn]:
            image, x, y = get_ship_image(ship, self.ship_images, 130, 50, 32, 1)
            self.screen.blit(image, (x - 2, y - 2))  # subtract 2 to centre on tiles

        # Draw the outline of the held ship.
        if self.held_ship is not None:
            col, row = snap_to_grid(self.mouse_x, self.mouse_y, 130, 50, 32)
            self.held_ship.origin_col, self.held_ship.origin_row = col, row

            image, x, y = get_ship_image(self.held_ship, self.ship_images, 130, 50, 32, 1)
            if check_ship_position(self.held_ship, self.p_arrangement[self.turn]) == 0:
                image.set_alpha(255)
                self.screen.blit(image, (x - 2, y - 2))  # subtract 2 to centre on tiles
            else:
                image.set_alpha(159)
                self.screen.blit(image, (self.mouse_x - 16, self.mouse_y - 16))

        # Draw the next ship to place.
        for i, ship in enumerate(self.p_stock_ships[self.turn]):
            image = self.ship_images[ship.name][1]
            if i == len(self.p_stock_ships[self.turn]) - 1:
                image.set_alpha(255)
            else:
                image.set_alpha(96)
            self.screen.blit(image, (8, display_height/3 + i*24))

        _message = "Player {0}'s Board: {1} ship{2} remaining".format(
            self.turn + 1, len(self.p_stock_ships[self.turn]),
            "s" if len(self.p_stock_ships[self.turn]) != 1 else ""
        )
        text.draw(self.screen, _message, (130, 30), color=C_LIGHT)

        if len(self.p_stock_ships[self.turn]) > 0:
            text.draw(self.screen, "Pick up a new ship by clicking over the left edge.",
                      (130, 390), color=C_LIGHT)
        if self.held_ship is not None or len(self.p_ships[self.turn]) > 0:
            text.draw(self.screen, "Click to pick up or place. R to rotate.",
                      (130, 410), color=C_LIGHT)

    def change_scene_menu(self):
        self.change_scene(ChooseMode)

    def confirm_layout(self):
        # This fail-safe check is used to make sure the player layout
        # is valid, as it may be possible to bypass the button-"enabled"
        # requirement by causing multiple events all in one frame.
        if not (len(self.p_stock_ships[self.turn]) == 0 and self.held_ship is None):
            return

        self.audio["cue"].play()
        if self.mode == ModeTwoPlayer and self.turn == 0:
            self.turn = 1  # allow other player to choose their arrangement
        else:
            if self.mode == ModeComputer:
                # Randomly generate a layout for player 2 (who is index 1).
                generate_computer_layout(self.p_ships[1], self.p_arrangement[1],
                                         self.p_stock_ships[1])
            self.change_scene(Game, self.mode, self.p_ships, self.p_arrangement, self.mute)

    def pick_ship(self):
        """Click over ship pick-up trigger: take ship from/return ship to queue."""
        if self.p_stock_ships[self.turn] and self.held_ship is None:
            self.held_ship = self.p_stock_ships[self.turn].pop()
        else:
            self.return_ship()

    def return_ship(self):
        """Clears the selected ship and places it back in the queue."""
        if self.held_ship is not None:
            self.p_stock_ships[self.turn].append(self.held_ship)
            self.held_ship = None

    def touch_grid(self):
        """Click over the grid: either place ship or take ship."""
        col, row = snap_to_grid(self.mouse_x, self.mouse_y, 130, 50, 32)

        if self.held_ship is None:
            # Check if any of the placed ships collide with the mouse pointer.
            for ship in self.p_ships[self.turn]:
                if (col, row) in ship.tile_indexes():
                    # Take ship and remove reference to deleted/moved ship.
                    remove_ship(ship, self.p_ships[self.turn], self.p_arrangement[self.turn])
                    self.held_ship = ship
        else:
            # Check if the chosen ship position is valid.
            self.held_ship.origin_col, self.held_ship.origin_row = col, row
            issue = check_ship_position(self.held_ship, self.p_arrangement[self.turn])

            if issue == 0:
                place_ship(self.held_ship, self.p_ships[self.turn],
                           self.p_arrangement[self.turn])
                self.held_ship = None
                self.audio["cue"].play()
            else:
                self.audio["alert"].play()

    def export_layout(self):
        print(encode_layout(self.p_ships[self.turn]).decode("utf-8"))

    def import_layout(self):
        ships_on_board = self.p_ships[self.turn]
        while ships_on_board:  # remove all ships that are currently placed
            remove_ship(ships_on_board[self.turn], ships_on_board, self.p_arrangement[self.turn])

        pg.event.pump()
        raw_string = input("Input string > ")
        try:
            for ship in decode_layout(bytes(raw_string, "utf-8")):
                place_ship(ship, ships_on_board, self.p_arrangement[self.turn])
        except ValueError:
            print("Failed to import ships. Please try again.")
        else:
            print(f"Successfully imported {len(ships_on_board)} ships!")
            self.p_stock_ships[self.turn].clear()
            self.confirm_layout()

    def sound_toggle(self, checked):
        self.mute = checked
        for sound in self.audio.values():
            if checked:
                sound.set_volume(0)
            else:
                sound.set_volume(100)

class Game(Scene):
    strike_font = pg.font.SysFont('Calibri', 20)

    def __init__(self, screen, clock, mode, player_ships, player_arrangement, mute=False):
        super().__init__(screen, clock)
        pg.display.set_caption("The Ocean")

        self.ship_images = load_ship_images()
        self.audio = load_audio()
        self.sound_toggle(mute)  # set sound to muted based on previous setting
        self.audio["begin"].play()

        self.mode = mode
        self.p_ships = player_ships
        self.p_arrangement = player_arrangement
        # Indicates which of your tiles have been revealed by the other player.
        self.p_revealed = (generate_blank_grid(False), generate_blank_grid(False))

        self.turn = 0  # 0 for player 1, 1 for player 2
        self.winner = None  # None for undecided, 0 for player 1, 1 for player 2

        if mode == ModeTwoPlayer:
            # Create 10*10 "tracking" grids for each player
            # to select opponent tiles to reveal.
            tracking_board_0 = TrackingBoard(30, 50, self.reveal, self.p_arrangement[1])
            tracking_board_1 = TrackingBoard(30, 50, self.reveal, self.p_arrangement[0])
            tracking_board_1.enabled = False

            self.add_mouse_handler(tracking_board_0)
            self.add_mouse_handler(tracking_board_1)
            self.tracking_boards = (tracking_board_0, tracking_board_1)

            # Create a button to switch turns.
            self.switch_turn_button = Button(
                (375, 370, 120, 28), "Next Turn", self.switch_turn, color=C_DARK,
                background=C_YELLOW, background_disabled=C_LIGHT_ISH)
            self.switch_turn_button.enabled = False
            self.add_mouse_handler(self.switch_turn_button)
        else:
            # Create 10*10 "tracking" grid for the player to select tiles to reveal.
            target = 0 if mode == ModeSingle else 1
            tracking_board_0 = TrackingBoard(30, 50, self.reveal,
                                             self.p_arrangement[target])
            self.add_mouse_handler(tracking_board_0)
            self.tracking_boards = (tracking_board_0, None)

        self.add_mouse_handler(Button((492, 5, 120, 28), "Back to Designer",
                               self.reset_game, color=C_DARK, background=C_LIGHT))

        if mode == ModeComputer:
            self.hide_ships = False
            # self.computer = ComputerPlayer(self.p_arrangement[0], self.p_revealed[0])
            self.computer = OpportunityPlayer(self.p_ships[0], self.p_arrangement[0], self.p_revealed[0])
        else:
            self.hide_ships = True

    def draw(self):
        self.screen.fill(C_LIGHT)
        for actor in self.actors:
            actor.draw(self.screen)

        # Draw the player's own 10*10 primary board.
        for x, y, col, row in layout_grid(375, 50, 24):
            # Colour and text is determined for each tile;
            # This depends on if it has been revealed and/or hides a ship.
            tile_is_part_of_ship = self.p_arrangement[self.turn][row][col] is not None

            if tile_is_part_of_ship and not self.hide_ships:
                if self.p_revealed[self.turn][row][col]:
                    ship_is_destroyed = self.p_arrangement[self.turn][row][col] \
                                            .destroyed(self.p_revealed[self.turn])
                    color = C_RED if ship_is_destroyed else C_YELLOW
                else:
                    color = C_LIGHT_GREEN
            else:
                color = C_DARK_BLUE if self.p_revealed[self.turn][row][col] else C_LIGHT_ISH

            pg.draw.rect(self.screen, color, (x, y, 21, 21))

        if not self.hide_ships or self.winner is not None:
            # Draw the ships.
            for ship in self.p_ships[self.turn]:
                image, x, y = get_ship_image(ship, self.ship_images, 375, 50, 24)
                image.set_alpha(249)
                self.screen.blit(image, (x - 2, y - 2))  # subtract 2 to centre on tiles
        elif self.mode == ModeTwoPlayer:
            hint_message = "The other player should click here:"
            text.draw(self.screen, hint_message, (375, 347), color=C_DARK_ISH)

        # Reveal any opponent ships that have been sunk too.
        for ship in self.p_ships[self.opponent()]:
            if ship.destroyed(self.p_revealed[self.opponent()]) or self.winner is not None:
                image, x, y = get_ship_image(ship, self.ship_images, 30, 50, 32)
                image.set_alpha(209)
                self.screen.blit(image, (x - 2, y - 2))  # subtract 2 to centre on tiles

        text.draw(self.screen, f"Player {self.turn + 1}'s turn", (30, 10), color=C_DARK)
        text.draw(self.screen, "Opponent's Grid", (30, 370),
                  color=C_DARK_ISH, static=True)
        text.draw(self.screen, "Your Grid", (375, 290),
                  color=C_DARK_ISH, static=True)

        timer_message = f"{self.clock.get_rawtime()}ms / frame"
        text.draw(self.screen, timer_message, (20, display_height - 20))

    def opponent(self):
        if self.mode == ModeSingle:
            return self.turn
        else:
            return not self.turn

    def reveal(self, col, row):
        self.p_revealed[self.opponent()][row][col] = True
        parent_ship = self.p_arrangement[self.opponent()][row][col]

        if parent_ship is not None:
            if parent_ship.destroyed(self.p_revealed[self.opponent()]):
                print(f"Hit: ship sunk!")
                for col, row in parent_ship.tile_indexes():
                    index = col*board_width + row
                    tile = self.tracking_boards[self.turn].tiles[index]
                    tile.style["background_disabled"] = C_RED

                self.audio["sink"].play()
                self.game_win_check()
            if not bonus_turn_on_hit or self.winner is not None:
                self.end_turn()
            self.audio["hit"].play()
        else:
            self.end_turn()
            self.audio["cue"].play()

    def game_win_check(self):
        if all(ship.destroyed(self.p_revealed[self.opponent()])
               for ship in self.p_ships[self.opponent()]) and self.winner is None:
            print("All ships destroyed.")
            self.add_mouse_handler(Button((375, 370, 120, 28), "Finish", self.reset_game,
                                          color=C_LIGHT, background=C_BLUEPRINT_BLUE))
            self.audio["begin"].play()
            self.winner = self.turn

            if self.mode == ModeTwoPlayer:
                self.tracking_boards[self.turn].disable_input = False
            else:
                self.tracking_boards[0].disable_input = True

    def end_turn(self):
        if self.mode == ModeTwoPlayer:
            # Blank the current player's board so the other player can't peek.
            self.hide_ships = True
            self.switch_turn_button.enabled = True

            # Disable the tracking board so the player can't reveal more than once.
            self.tracking_boards[self.turn].disable_input = True

        elif self.mode == ModeComputer:
            col, row = self.computer.play_move()
            if col is None or row is None:
                return

            self.p_revealed[0][row][col] = True
            parent_ship = self.p_arrangement[0][row][col]

            if parent_ship is not None and parent_ship.destroyed(self.p_revealed[0]):
                self.turn = int(not self.turn)
                self.game_win_check()
                self.turn = int(not self.turn)
                self.audio["sink"].play()

        else:  # in single board mode, there are no turn transfers.
            return

    def switch_turn(self):
        self.turn = int(not self.turn)
        # Enable the current player's boards.
        self.tracking_boards[self.turn].enabled = True
        self.tracking_boards[not self.turn].enabled = False

        self.switch_turn_button.enabled = False
        self.tracking_boards[not self.turn].disable_input = False
        self.hide_ships = False

    def sound_toggle(self, checked):
        self.mute = checked  # toggle the value of "sound muted"
        for sound in self.audio.values():
            if checked:
                sound.set_volume(0)
            else:
                sound.set_volume(100)

    def reset_game(self):
        self.change_scene(Setup, self.mode, self.p_ships, self.p_arrangement, self.mute)

def cause_quit_event():
    """Push a QUIT event onto the event queue, which is registered by the main loop."""
    pg.event.post(pg.event.Event(pg.QUIT, {}))
