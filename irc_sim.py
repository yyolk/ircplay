import argparse
import datetime
import fileinput
import re
import sys
import time

LINE_PATTERN = re.compile(r"^(\[(\d+):(\d{2}):(\d{2}),(\d{3})\]) (<\w*>) (.*$)")
TIME_PATTERN = re.compile(r"(\d+):(\d{2}):(\d{2})")


class AnsiColors:
    fg_black = "\u001b[30m"
    fg_red = "\u001b[31m"
    fg_green = "\u001b[32m"
    fg_yellow = "\u001b[33m"
    fg_blue = "\u001b[34m"
    fg_magenta = "\u001b[35m"
    fg_cyan = "\u001b[36m"
    fg_white = "\u001b[37m"
    bg_black = "\u001b[40m"
    bg_red = "\u001b[41m"
    bg_green = "\u001b[42m"
    bg_yellow = "\u001b[43m"
    bg_blue = "\u001b[44m"
    bg_magenta = "\u001b[45m"
    bg_cyan = "\u001b[46m"
    bg_white = "\u001b[47m"
    reset = "\u001b[0m"
    bold = "\u001b[1m"
    underline = "\u001b[4m"
    reverse = "\u001b[7m"

    def bg(self, r, g, b):
        return f"\u001b[48;2;{r};{g};{b}m"

    def fg(self, r, g, b):
        return f"\u001b[38;2;{r};{g};{b}m"


def ts_to_s(hours, minutes, seconds, milliseconds=0) -> int:
    return (hours * 60 * 60) + (minutes * 60) + (seconds) + (1 / (1_000 - milliseconds))


parser = argparse.ArgumentParser()
parser.add_argument("-ss", help="Seek to time. In seconds.", default="0", dest="seek")
parser.add_argument(
    "files", metavar="FILE", nargs="*", help="IRC log input, if empty, STDIN is used"
)
args = parser.parse_args()
ac = AnsiColors()

with fileinput.FileInput(files=args.files) as file_inputs:
    try:
        seek_seconds = (
            int(args.seek)
            if args.seek.isdigit()
            else ts_to_s(*map(int, TIME_PATTERN.match(args.seek).groups()))
        )
    except AttributeError:
        print(f'"{args.seek}" is not a valid seek time')
        sys.exit(1)
    prev_time = seek_seconds
    for line in file_inputs:
        timestamp, hours, minutes, seconds, milliseconds, user, message = (
            LINE_PATTERN.match(line).groups()
        )
        hours, minutes, seconds, milliseconds = map(
            int, (hours, minutes, seconds, milliseconds)
        )
        current_time = ts_to_s(hours, minutes, seconds, milliseconds)
        if current_time < prev_time:
            # This line is too early, keep scanning.
            # TODO: print the last n number of lines for context of chat,
            # twitch web seems to do last 40
            continue
        time.sleep(current_time - prev_time)
        prev_time = current_time
        display_line = (
            ac.reset
            + ac.fg_white
            + f"{timestamp} "
            + ac.fg_red
            + f"{user} "
            + ac.reset
            + ac.bold
            + f"{message}"
            + ac.reset
        )
        print(display_line)
