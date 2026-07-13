import time
import curses
import random

from global_state import coroutines, obstacles_list, obstacles_in_last_collisions, year
import curses_tutorial
import space_ship
import fly_garbage
from timeline import show_years


TIC_TIMEOUT = 0.1



def draw(canvas):
    global coroutines
    canvas.border()
    curses.curs_set(False)
    window = curses.initscr()
    window.nodelay(True)
    max_row, max_column = window.getmaxyx()
    middle_row, middle_column = max_row / 2, max_column / 2
    space_ship_animation = space_ship.animate_spaceship(canvas, middle_row, middle_column, coroutines)
    coroutines.append(space_ship_animation)
    fill_orbit = fly_garbage.fill_orbit_with_garbage(canvas, max_column, coroutines)
    coroutines.append(fill_orbit)
    year_counter = show_years(canvas)
    coroutines.append(year_counter)
    stars = ['+', '*', '.', ':']
    max_star_row, max_star_col = curses_tutorial.get_star_borders(stars)
    for star in range(100):
        star = curses_tutorial.blink(canvas,
                     random.randint(max_star_row, max_row - max_star_row),
                     random.randint(max_star_col, max_column - max_star_col),
                     symbol=random.choice(stars))
        coroutines.append(star)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)




if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
