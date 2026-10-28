import curses
from curses import wrapper

def main(stdscr):
    curses.init_pair(1,curses.COLOR_RED,curses.COLOR_GREEN)
    

wrapper(main)
