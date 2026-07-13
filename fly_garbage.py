import asyncio
import random

from global_state import obstacles_list, obstacles_in_last_collisions, coroutines, year
import obstacles
import curses_tutorial
import explosion
from timeline import get_garbage_delay_tics, get_year


with open('animation/trash_large.txt', "r") as garbage_file:
  frame_large = garbage_file.read()

with open('animation/trash_small.txt', "r") as garbage_file:
  frame_small = garbage_file.read()

with open('animation/trash_xl.txt', "r") as garbage_file:
  frame_xl = garbage_file.read()


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



async def fill_orbit_with_garbage(canvas, max_column, coroutines):
    while True:
        year = get_year()
        delay = get_garbage_delay_tics(year)
        if delay:
            await curses_tutorial.sleep(delay/10)
            garbage = animate_garbage(canvas, max_column)
            coroutines.append(garbage)
        await asyncio.sleep(0)


async def animate_garbage(canvas, max_column):
    garbage_frames = [frame_large, frame_small, frame_xl]
    random_column = random.randint(2, max_column - 2)
    random_garbage = random.choice(garbage_frames)
    await asyncio.sleep(0)
    await fly_garbage(canvas, random_column, random_garbage)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    rows_size, columns_size = curses_tutorial.get_frame_size(garbage_frame)
    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    obstacle = obstacles.Obstacle(row, column, rows_size, columns_size)
    obstacles_list.append(obstacle)
    try:
        while row < rows_number:
            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                garbage_explosion = explosion.explode(canvas, row, column)
                coroutines.append(garbage_explosion)
                return
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            obstacle.row += speed
            row += speed
    finally:
        obstacles_list.remove(obstacle)
