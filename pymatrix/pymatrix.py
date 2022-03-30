#! /usr/bin/python3
""" Matrix style rain using Python 3 and curses. """
import argparse
import curses
import datetime
import sys

from random import choice
from random import randint
from time import sleep

from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

version = importlib_metadata.version("pymatrix-rain")

CHAR_LIST = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
             "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B",
             "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
             "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3",
             "4", "5", "6", "7", "8", "9", "!", "#", "$", "%", "^", "&", "(", ")",
             "-", "+", "=", "[", "]", "{", "}", "|", ";", ":", "<", ">", ",", ".",
             "?", "~", "`", "@", "*", "_", "'", "\\", "/", '"', "ç" "λ", "μ", "π", 
             "Σ", "Ω", "ｦ", "ｱ", "ｲ", "ｳ", "ｵ", "ｶ", "ｷ", "ｸ", "ｹ", "ｺ", "ｻ", "ｼ", 
             "ｽ", "ｾ", "ｿ", "ﾀ", "ﾁ", "ﾂ", "ﾃ", "ﾄ", "ﾅ", "ﾆ", "ﾇ", "ﾈ", "ﾉ", "ﾊ", 
             "ﾋ", "ﾌ", "ﾍ", "ﾎ", "ﾏ", "ﾐ", "ﾑ", "ﾒ", "ﾓ", "ﾔ", "ﾕ", "ﾖ", "ﾗ", "ﾘ", 
             "ﾙ", "ﾚ", "ﾛ", "ﾜ", "ﾝ"]

EXT_INTS = [199, 200, 204, 205, 208, 209, 210, 215, 216, 217, 218, 221, 222, 223, 224,
            163, 164, 165, 167, 170, 182, 186, 187, 191, 196, 197, 233, 234, 237, 239,
            229, 230, 231, 232, 240, 241, 242, 246, 248, 249, 253, 254, 257, 263, 265,
            279, 283, 285, 291, 295, 299, 305, 311, 317, 321, 322, 324, 328, 333, 338,
            339, 341, 343, 347, 349, 353, 357, 363, 371, 376, 378, 380, 381, 382, 537,
            539, 35]
EXT_CHAR_LIST = [chr(x) for x in EXT_INTS]

DELAY_SPEED = {0: 0.005, 1: 0.01, 2: 0.025, 3: 0.04, 4: 0.055, 5: 0.07,
               6: 0.085, 7: 0.1, 8: 0.115, 9: 0.13}

CURSES_CH_CODES_DELAY = {
    48: 0, 49: 1, 50: 2, 51: 3, 52: 4, 53: 5, 54: 6, 55: 7, 56: 8, 57: 9
}
CURSES_CH_CODES_CYCLE_DELAY = {41: 1, 33: 2, 64: 3, 35: 4, 36: 5, 37: 6,
                               94: 7, 38: 8, 42: 9, 40: 10}

CURSES_COLOR = {"red": curses.COLOR_RED, "green": curses.COLOR_GREEN,
                "blue": curses.COLOR_BLUE, "yellow": curses.COLOR_YELLOW,
                "magenta": curses.COLOR_MAGENTA, "cyan": curses.COLOR_CYAN,
                "white": curses.COLOR_WHITE, "black": curses.COLOR_BLACK}

CURSES_CH_CODES_COLOR = {114: "red", 82: "red", 116: "green", 84: "green",
                         121: "blue", 89: "blue", 117: "yellow", 85: "yellow",
                         105: "magenta", 73: "magenta", 111: "cyan",
                         79: "cyan", 112: "white", 80: "white", 18: "red",
                         20: "green", 25: "blue", 21: "yellow", 9: "magenta",
                         15: "cyan", 16: "white", 27: "black", 91: "black", 123: "black"}

MIN_SCREEN_SIZE_Y = 10
MIN_SCREEN_SIZE_X = 10


class PyMatrixError(Exception):
    pass


class SingleLine:
    async_scroll = False
    extended_char = "off"
    char_list = CHAR_LIST

    def __init__(self, x: int, width: int, height: int, reverse: bool) -> None:
        self.reverse = reverse
        if self.reverse:
            self.y = height - 2
            self.x = x
            self.lead_y = height - 3
            self.length = randint(3, height - 3)
            self.data = []
            self.width = width
            self.height = height - 2
            self.line_color_number = randint(1, 7)
            self.async_scroll_rate = randint(0, 3)
            self.async_scroll_position = 0
        else:
            self.y = -1
            self.x = x
            self.length = randint(3, height - 3)
            self.data = []
            self.lead_y = 0
            self.width = width
            self.height = height - 2
            self.line_color_number = randint(1, 7)
            self.async_scroll_rate = randint(0, 3)
            self.async_scroll_position = 0

    def increment(self) -> None:
        """ moves the lead y position and y position """
        if self.reverse:
            if self.lead_y >= 0:
                self.lead_y -= 1
            if self.y >= 0:
                self.y -= 1
        else:
            if self.lead_y <= self.height:
                self.lead_y += 1
            if self.y <= self.height:
                self.y += 1

    def async_scroll_turn(self) -> bool:
        """ Checks to see if lines turn when async like scrolling is on"""
        if self.async_scroll_position == self.async_scroll_rate:
            self.async_scroll_position = 0
            return True
        else:
            self.async_scroll_position += 1
            return False

    def add_char(self) -> None:
        """ Adds a random char to the line """
        if self.reverse:
            if self.y > 0:
                self.data.append((self.y, choice(SingleLine.char_list)))
            else:
                return None
        else:
            if 0 <= self.y <= self.height:
                self.data.append((self.y, choice(SingleLine.char_list)))
            else:
                return None

    def get_new(self) -> Union[Tuple[int, int, str], None]:
        """ Gets the last char that was added"""
        if self.reverse:
            if self.y > 0 and len(self.data) > 0:
                new = (self.data[-1][0], self.x, self.data[-1][1])
                return new
            else:
                return None
        else:
            if 0 <= self.y <= self.height and len(self.data) > 0:
                new = (self.data[-1][0], self.x, self.data[-1][1])
                return new
            else:
                return None

    def get_lead(self) -> Union[Tuple[int, int, str], None]:
        """ Gets the lead char """
        if self.reverse:
            if self.lead_y > 0:
                return self.lead_y, self.x, choice(SingleLine.char_list)
            else:
                return None
        else:
            if self.lead_y < self.height:
                return self.lead_y, self.x, choice(SingleLine.char_list)
            else:
                return None

    def get_remove(self) -> Union[Tuple[int, int, str], None]:
        """ Remove char from list and returns the location to erase """
        data_len = len(self.data)
        if self.reverse:
            if data_len >= self.length or self.y <= 0:
                rm = (self.data[0][0], self.x, " ")  # 1
                self.data.pop(0)
                return rm
            elif self.y <= 0 < data_len:
                rm = (self.data[0][0], self.x, " ")
                self.data.pop(0)
                return rm
            return None
        else:
            if data_len >= self.length or self.y >= self.height and data_len >= 0:
                rm = (self.data[0][0], self.x, " ")
                self.data.pop(0)
                return rm
            elif data_len > 0 and self.data[0][0] >= self.height:
                rm = (self.data[0][0], self.x, " ")
                self.data.pop(0)
                return rm
            return None

    @classmethod
    def set_test_mode(cls, test_mode: bool, extended: bool) -> None:
        if test_mode and extended:
            cls.char_list = ["T", chr(35)]
        elif test_mode:
            cls.char_list = ["T"]
        elif extended:
            cls.char_list = [chr(35)]
        else:
            cls.char_list = CHAR_LIST

    @classmethod
    def set_extended_chars(cls, state: str):
        # off, on, only
        if state == "off":
            cls.extended_char = "off"
            cls.char_list = CHAR_LIST
        elif state == "on":
            cls.extended_char = "on"
            cls.char_list = CHAR_LIST + EXT_CHAR_LIST
        elif state == "only":
            cls.extended_char = "only"
            cls.char_list = EXT_CHAR_LIST

    @classmethod
    def set_zero_one(cls, mode: bool):
        if mode:
            cls.char_list = ["0", "1"]
        else:
            cls.char_list = CHAR_LIST

# Fury Changes (Half-width kana)
    @classmethod
    def set_hankaku_kana(cls, mode: bool):
        if mode:
            cls.char_list = ["ｦ", "ｱ", "ｲ", "ｳ", "ｵ", "ｶ", "ｷ", "ｸ", 
                            "ｹ", "ｺ", "ｻ", "ｼ", "ｽ", "ｾ", "ｿ", "ﾀ", 
                            "ﾁ", "ﾂ", "ﾃ", "ﾄ", "ﾅ", "ﾆ", "ﾇ", "ﾈ", 
                            "ﾉ", "ﾊ", "ﾋ", "ﾌ", "ﾍ", "ﾎ", "ﾏ", "ﾐ", 
                            "ﾑ", "ﾒ", "ﾓ", "ﾔ", "ﾕ", "ﾖ", "ﾗ", "ﾘ",
                            "ﾙ", "ﾚ", "ﾛ", "ﾜ", "ﾝ"]
        else:
            cls.char_list = CHAR_LIST

def matrix_loop(screen, args: argparse.Namespace) -> None:
    """ Main loop. """
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    setup_curses_colors(args.color, args.background)
    curses_lead_color(args.lead_color, args.background)
    screen.bkgd(" ", curses.color_pair(1))
    count = cycle = 0  # used for cycle through colors mode
    cycle_delay = 500
    line_list = []
    spacer = 2 if args.double_space else 1
    keys_pressed = 0
    if args.ext:
        SingleLine.set_extended_chars("on")
    if args.ext_only:
        SingleLine.set_extended_chars("only")

    if args.async_scroll:
        SingleLine.async_scroll = True
    if args.test_mode or args.test_mode_ext:
        SingleLine.set_test_mode(args.test_mode, args.test_mode_ext)

    if args.test_mode:
        wake_up_time = 20
    else:
        wake_up_time = randint(2000, 3000)

    if args.zero_one:
        SingleLine.set_zero_one(True)

# FIX
    #if args.hankaku_kana:
     #   SingleLine.set_hankaku_kana(True)

    if args.multiple_mode:
        color_mode = "multiple"
        setup_curses_colors("random", args.background)
    elif args.random_mode:
        color_mode = "random"
        setup_curses_colors("random", args.background)
    elif args.cycle:
        color_mode = "cycle"
    else:
        color_mode = "normal"

    size_y, size_x = screen.getmaxyx()
    if size_y < MIN_SCREEN_SIZE_Y:
        raise PyMatrixError("Error screen height is to short.")
    if size_x < MIN_SCREEN_SIZE_X:
        raise PyMatrixError("Error screen width is to narrow.")
    x_list = [x for x in range(0, size_x, spacer)]

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=args.run_timer)
    while True:
        remove_list = []
        if len(line_list) < size_x - 1 and len(x_list) > 3:
            for _ in range(2):
                x = choice(x_list)
                x_list.pop(x_list.index(x))
                line_list.append(SingleLine(x, size_x, size_y, args.reverse))

        resize = curses.is_term_resized(size_y, size_x)
        if resize is True:
            size_y, size_x = screen.getmaxyx()
            if size_y < MIN_SCREEN_SIZE_Y:
                raise PyMatrixError("Error screen height is to short.")
            if size_x < MIN_SCREEN_SIZE_X:
                raise PyMatrixError("Error screen width is to narrow.")
            x_list = [x for x in range(0, size_x, spacer)]

            line_list.clear()
            screen.clear()
            screen.refresh()
            continue

        if color_mode == "cycle":
            if count <= 0:
                setup_curses_colors(list(CURSES_COLOR.keys())[cycle], args.background)
                count = cycle_delay
                cycle = 0 if cycle == 6 else cycle + 1
            else:
                count -= 1

        for line in line_list:
            if SingleLine.async_scroll and not line.async_scroll_turn():
                # Not the line's turn in async scroll mode then continue to the next line.
                continue
            line.add_char()
            remove_line = line.get_remove()
            if remove_line:
                screen.addstr(remove_line[0], remove_line[1], remove_line[2])
                if line.x not in x_list:
                    x_list.append(line.x)

            if args.bold_all:
                bold = curses.A_BOLD
            elif args.bold_on:
                bold = curses.A_BOLD if randint(1, 3) <= 1 else curses.A_NORMAL
            else:
                bold = curses.A_NORMAL

            new_char = line.get_new()
            if new_char:
                if color_mode == "random":
                    color = curses.color_pair(randint(1, 7))
                else:
                    color = curses.color_pair(line.line_color_number)
                screen.addstr(new_char[0], new_char[1], new_char[2], color + bold)

            lead_char = line.get_lead()
            if lead_char:
                screen.addstr(lead_char[0], lead_char[1], lead_char[2],
                              curses.color_pair(10) + bold)

            line.increment()
            if line.reverse and len(line.data) <= 0 and line.y <= 0:
                remove_list.append(line)
            elif len(line.data) <= 0 and line.y >= size_y - 2:
                remove_list.append(line)
        screen.refresh()

        for rem in remove_list:
            line_list.pop(line_list.index(rem))
            x_list.append(rem.x)

        if args.wakeup:
            if wake_up_time <= 0:
                wake_up_neo(screen, args.test_mode)
                wake_up_time = randint(2000, 3000)
                _ = screen.getch()
                screen.bkgd(" ", curses.color_pair(1))
                _ = screen.getch()  # clears out any saved key presses
            else:
                wake_up_time -= 1

        if args.run_timer and datetime.datetime.now() >= end_time:
            break
        ch = screen.getch()
        if args.screen_saver and ch != -1:
            break
        if ch in [81, 113]:  # q, Q
            break
        elif ch != -1 and not args.disable_keys:
            # Commands:
            if ch == 119 and keys_pressed == 0:  # w
                keys_pressed = 1
            elif ch == 65 and keys_pressed == 1:  # A
                keys_pressed = 2
            elif ch == 107 and keys_pressed == 2:  # k
                keys_pressed = 3
            elif ch == 101 and keys_pressed == 3:  # e
                wake_up_neo(screen, args.test_mode)
                _ = screen.getch()  # clears out any saved key presses
                keys_pressed = 0
                screen.bkgd(" ", curses.color_pair(1))
                continue
            else:
                keys_pressed = 0
            if ch == 98:  # b
                args.bold_on = True
                args.bold_all = False
            elif ch == 66:  # B
                args.bold_all = True
                args.bold_on = False
            elif ch in [78, 110]:  # n or N
                args.bold_on = False
                args.bold_all = False
            elif ch in [114, 116, 121, 117, 105, 111, 112, 91]:
                # r, t, y, u, i, o, p, [
                args.color = CURSES_CH_CODES_COLOR[ch]
                setup_curses_colors(args.color, args.background)
                color_mode = "normal"
            elif ch in [82, 84, 89, 85, 73, 79, 80, 123]:
                # R, T, Y, U, I, O, P, {
                args.lead_color = CURSES_CH_CODES_COLOR[ch]
                curses_lead_color(args.lead_color, args.background)
            elif ch in [18, 20, 25, 21, 9, 15, 16, 27]:
                # ctrl R, T, Y, U, I, O, P, [
                args.background = CURSES_CH_CODES_COLOR[ch]
                setup_curses_colors(args.color, args.background)
                curses_lead_color(args.lead_color, args.background)
                screen.bkgd(" ", curses.color_pair(1))
            elif ch == 97:  # a
                SingleLine.async_scroll = not SingleLine.async_scroll
            elif ch == 109:  # m
                if color_mode in ["random", "normal", "cycle"]:
                    color_mode = "multiple"
                    setup_curses_colors("random", args.background)
                else:
                    color_mode = "normal"
                    setup_curses_colors("green", args.background)
            elif ch == 77:  # M
                if color_mode in ["multiple", "normal", "cycle"]:
                    color_mode = "random"
                    setup_curses_colors("random", args.background)
                else:
                    color_mode = "normal"
                    setup_curses_colors("green", args.background)
            elif ch == 99:  # c
                if color_mode in ["random", "multiple", "normal"]:
                    color_mode = "cycle"
                else:
                    color_mode = "normal"
            elif ch == 108:  # l
                if spacer == 1:
                    spacer = 2
                    x_list = [x for x in range(0, size_x, spacer)]
                    line_list.clear()
                    screen.clear()
                    screen.refresh()
                else:
                    spacer = 1
                    x_list = [x for x in range(0, size_x, spacer)]
            elif ch == 101:  # e
                if SingleLine.extended_char == "off":
                    SingleLine.set_extended_chars("on")
                else:
                    SingleLine.set_extended_chars("off")
            elif ch == 69:  # E
                if SingleLine.extended_char == "on":
                    SingleLine.set_extended_chars("only")
                elif SingleLine.extended_char == "only":
                    SingleLine.set_extended_chars("on")
            elif ch == 122 and not args.zero_one:  # z
                SingleLine.set_zero_one(True)
                line_list.clear()
                screen.clear()
                screen.refresh()
                args.zero_one = True
            elif ch == 90 and args.zero_one:  # Z
                SingleLine.set_zero_one(False)
                line_list.clear()
                screen.clear()
                screen.refresh()
                args.zero_one = False
            elif ch == 104 and not args.hankaku_kana:  # h
                SingleLine.set_hankaku_kana(True)
                line_list.clear()
                screen.clear()
                screen.refresh()
                args.hankaku_kana = True
            elif ch == 72 and args.hankaku_kana:  # H
                SingleLine.set_hankaku_kana(False)
                line_list.clear()
                screen.clear()
                screen.refresh()
                args.hankaku_kana = False
            elif ch == 23:  # ctrl-w
                args.wakeup = not args.wakeup
            elif ch == 118:  # v
                args.reverse = not args.reverse
                line_list.clear()
                screen.clear()
                screen.refresh()
            elif ch in [100, 68]:  # d, D
                SingleLine.set_zero_one(False)
                SingleLine.set_hankaku_kana(False)
                args.zero_one = False
                args.hankaku_kana = False
                args.bold_on = False
                args.bold_all = False
                args.background = "black"
                args.color = "green"
                args.lead_color = "white"
                setup_curses_colors(args.color, args.background)
                curses_lead_color(args.lead_color, args.background)
                color_mode = "normal"
                SingleLine.async_scroll = False
                args.delay = 4
                SingleLine.set_extended_chars("off")
                if spacer == 2:
                    spacer = 1
                    x_list = [x for x in range(0, size_x, spacer)]
                if args.reverse:
                    args.reverse = False
                    line_list.clear()
                    screen.clear()
                    screen.refresh()
            elif color_mode == "cycle" and ch in CURSES_CH_CODES_CYCLE_DELAY.keys():
                cycle_delay = 100 * CURSES_CH_CODES_CYCLE_DELAY[ch]
                count = cycle_delay
            elif ch in CURSES_CH_CODES_DELAY.keys():
                args.delay = CURSES_CH_CODES_DELAY[ch]
            elif ch == 102:  # f
                # Freeze the Matrix
                quit_matrix = False
                while True:
                    ch = screen.getch()
                    if ch == 102:
                        break
                    elif ch in [81, 113]:  # q, Q
                        quit_matrix = True
                        break
                if quit_matrix:
                    break
        sleep(DELAY_SPEED[args.delay])

    screen.erase()
    screen.refresh()


def curses_lead_color(color: str, background_color: str) -> None:
    curses.init_pair(10, CURSES_COLOR[color], CURSES_COLOR[background_color])


def setup_curses_colors(color: str, background_color: str) -> None:
    """ Init colors pairs in the curses. """
    if color == "random":
        color_list = list(CURSES_COLOR.keys())
    else:
        color_list = [color for _ in range(7)]

    for x, c in enumerate(color_list):
        curses.init_pair(x + 1, CURSES_COLOR[c], CURSES_COLOR[background_color])
    curses.init_pair(21, curses.COLOR_GREEN, curses.COLOR_BLACK)


def wake_up_neo(screen, test_mode: bool) -> None:
    z = 0.06 if test_mode else 1  # Test mode off set. To make test time shorter.
    screen.erase()
    # screen.refresh()
    screen.bkgd(" ", curses.color_pair(21))
    screen.refresh()
    sleep(3 * z)
    display_text(screen, "Wake up, Neo...", 0.08 * z, 7.0 * z)
    display_text(screen, "The Matrix has you...", 0.25 * z, 7.0 * z)
    display_text(screen, "Follow the white rabbit.", 0.1 * z, 7.0 * z)
    display_text(screen, "Knock, knock, Neo.", 0.01 * z, 3.0 * z)
    sleep(2 * z)


def display_text(screen, text: str, type_time: float, hold_time: float) -> None:
    for i, letter in enumerate(text, start=1):
        screen.addstr(1, i, letter, curses.color_pair(21) + curses.A_BOLD)
        screen.refresh()
        sleep(type_time)
    sleep(hold_time)
    screen.erase()
    screen.refresh()


def positive_int_zero_to_nine(value: str) -> int:
    """
    Used with argparse.
    Checks to see if value is positive int between 0 and 10.
    """
    try:
        int_value = int(value)
        if int_value < 0 or int_value >= 10:
            raise argparse.ArgumentTypeError(f"{value} is an invalid positive "
                                             f"int value 0 to 9")
        return int_value
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int "
                                         f"value 0 to 9")


def color_type(value: str) -> str:
    """
    Used with argparse
    Checks to see if the value is a valid color and returns
    the lower case color name.
    """
    lower_value = value.lower()
    if lower_value in CURSES_COLOR.keys():
        return lower_value
    raise argparse.ArgumentTypeError(f"{value} is an invalid color name")


def positive_int(value: str) -> int:
    """
    Used by argparse.
    Checks to see if the value is positive.
    """
    try:
        int_value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    else:
        if int_value <= 0:
            raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return int_value


def display_commands() -> None:
    print("Commands available during run")
    print("0 - 9  Delay time (0-Fast, 4-Default, 9-Slow)")
    print("b      Bold characters on")
    print("B      Bold all characters")
    print("n      Bold off (Default)")
    print("a      Asynchronous like scrolling")
    print("m      Multiple color mode")
    print("M      Multiple random color mode")
    print("c      Cycle colors")
    print("d      Restore all defaults")
    print("l      Toggle double space lines")
    print("e      Extended characters on and off")
    print("E      Extended characters only")
    print("z      1 and 0 Mode On")
    print("Z      1 and 0 Mode Off")
    print("f      Freeze the matrix (q will still quit")
    print("v      Toggle matrix scrolling up")
    print("r,t,y,u,i,o,p,[   Set color")
    print("R,T,Y,U,I,O,P,{   Set lead character color")
    print("ctrl + r,t,y,u,i,o,p,[  Set background color")
    print("shift 0 - 9 Cycle color delay (0-Fast, 4-Default, 9-Slow)")


def argument_parsing(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """ Command line argument parsing. """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", dest="delay", type=positive_int_zero_to_nine, default=4,
                        help="Set the delay (speed) 0: Fast, 4: Default, 9: Slow")
    parser.add_argument("-b", dest="bold_on", action="store_true",
                        help="Bold characters on")
    parser.add_argument("-B", dest="bold_all", action="store_true",
                        help="All bold characters (overrides -b)")
    parser.add_argument("-s", dest="screen_saver", action="store_true",
                        help="Screen saver mode.  Any key will exit.")
    parser.add_argument("-a", dest="async_scroll", action="store_true",
                        help="enable asynchronous like scrolling")
    parser.add_argument("-S", dest="start_timer", type=positive_int, default=0,
                        metavar="SECONDS", help="Set start timer in seconds")
    parser.add_argument("-R", dest="run_timer", type=positive_int, default=0,
                        metavar="SECONDS", help="Set run timer in seconds")
    parser.add_argument("-C", dest="color", type=color_type, default="green",
                        help="Set color.  Default is green")
    parser.add_argument("-L", dest="lead_color", type=color_type, default="white",
                        help="Set the lead character color.  Default is white")
    parser.add_argument("-m", dest="multiple_mode", action="store_true",
                        help="Multiple color mode")
    parser.add_argument("-M", dest="random_mode", action="store_true",
                        help="Multiple random color mode")
    parser.add_argument("-c", dest="cycle", action="store_true",
                        help="cycle through the colors")
    parser.add_argument("-e", dest="ext", action="store_true",
                        help="use extended characters")
    parser.add_argument("-E", dest="ext_only", action="store_true",
                        help="use only extended characters (overrides -e)")
    parser.add_argument("-l", dest="double_space", action="store_true",
                        help="Double space lines")
    parser.add_argument("-z", dest="zero_one", action="store_true",
                        help="Show only zero and ones. Binary")
    parser.add_argument("--background", type=color_type, default="black",
                        help="set background color. Default is black.")
    parser.add_argument("-v", "--reverse", action="store_true",
                        help="Reverse the matrix. The matrix scrolls up (vertical)")
    parser.add_argument("--disable_keys", action="store_true",
                        help="Disable keys except for Q to quit. Screensaver mode will"
                             "not be affected")
    parser.add_argument("--list_colors", action="store_true",
                        help="Show available colors and exit. ")
    parser.add_argument("--list_commands", action="store_true",
                        help="List Commands and exit")
    parser.add_argument("--version", action="version", version=f"Version: {version}")

    parser.add_argument("--wakeup", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--test_mode", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--test_mode_ext", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = argument_parsing(argv)

    if args.list_colors:
        print(*CURSES_COLOR.keys())
        return
    if args.list_commands:
        display_commands()
        return

    sleep(args.start_timer)
    try:
        curses.wrapper(matrix_loop, args)
    except KeyboardInterrupt:
        pass
    except PyMatrixError as e:
        print(e)
        return


if __name__ == "__main__":
    main()
