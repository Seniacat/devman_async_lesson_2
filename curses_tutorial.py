import asyncio
import time
import curses
import random


async def sleep(ticks):
    ticks = int(ticks*10)
    for i in range(ticks):
        await asyncio.sleep(0)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def blink(canvas, row, column, symbol):
    """Display animation of stars."""
    curses_list = [curses.A_DIM, 0, curses.A_BOLD, 0]
    while True:
        for param in curses_list:
            canvas.addstr(row, column, symbol, param)
            await sleep((random.randint(2, 20)) / 10)


def get_star_borders(stars):
    star_sizes_list = [get_frame_size(star) for star in stars]
    max_star_row = max([size[0] for size in star_sizes_list])
    max_star_col = max([size[1] for size in star_sizes_list])
    return max_star_row, max_star_col


