import asyncio
import time
import curses
import random

import physics
import curses_tutorial
from global_state import obstacles_list, obstacles_in_last_collisions, gun_enabled, game_over
from timeline import get_year


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258



with open('animation/rocket_frame_1.txt',
          'r') as file:
    frame_1 = file.read()

with open('animation/rocket_frame_2.txt',
          'r') as file:
    frame_2 = file.read()

with open('animation/game_over.txt',
          'r') as file:
    game_over_frame = file.read()


async def sleep(ticks):
   for i in range(ticks):
        await asyncio.sleep(0)


def process_control(canvas, row, column, row_delta, column_delta, row_speed, column_speed):
    max_row, max_column = canvas.getmaxyx()
    rows_direction, columns_direction, space_pressed = read_controls(canvas)
    row_speed, column_speed = physics.update_speed(row_speed, column_speed, rows_direction, columns_direction)
    new_row, new_column = row + row_speed, column + column_speed
    #new_row = row + rows_direction
    #new_column = column + columns_direction
    if new_row < 0 or new_row > (max_row - row_delta):
        new_row = row
    if new_column < 0 or new_column > (max_column - column_delta):
        new_column = column
    return new_row, new_column, row_speed, column_speed, space_pressed


def get_gun_state():
    global gun_enabled
    current_year = get_year()
    if current_year >= 2020:
        gun_enabled = True
    return gun_enabled

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns + 2

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        for obstacle in obstacles_list:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return
        row += rows_speed
        column += columns_speed


async def rocket_animation():
    rocket_frames = [frame_1, frame_1, frame_2, frame_2]
    while True:
        for frame in rocket_frames:
            await sleep(0)
            yield frame


async def show_game_over(canvas):
    height, width = canvas.getmaxyx()
    rows_size, columns_size = curses_tutorial.get_frame_size(game_over_frame)
    row = (height - rows_size) // 2
    column = (width - columns_size) // 2

    while True:
        draw_frame(canvas, row, column, game_over_frame)
        await asyncio.sleep(0)


async def animate_spaceship(canvas, row, column, coroutines):
    global game_over
    rows_speed = columns_speed = 0
    async for frame in rocket_animation():
        frame_rows, frame_columns = get_frame_size(frame)
        prev_row, prev_col = row - frame_rows/2, column - frame_columns/2
        for obstacle in obstacles_list:
            if obstacle.has_collision(row, column):
                game_over = True
                coroutines.append(show_game_over(canvas))
                return
        row, column, rows_speed, columns_speed, space_pressed = process_control(
            canvas,
            row,
            column,
            frame_rows,
            frame_columns,
            rows_speed,
            columns_speed
        )
        draw_frame(canvas, prev_row, prev_col, frame)
        await sleep(1)
        draw_frame(canvas, prev_row, prev_col, frame, negative=True)
        draw_frame(canvas, prev_row, prev_col, frame)
        draw_frame(canvas, prev_row, prev_col, frame, negative=True)
        gun_state = get_gun_state()
        if space_pressed and gun_state:
            coroutines.append(fire(canvas, row, column))


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


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

