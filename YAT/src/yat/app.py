import curses
import time
import pyte
from yat.backend import YATBackend

SPECIAL_KEYS = {
    curses.KEY_UP: '\x1b[A',
    curses.KEY_DOWN: '\x1b[B',
    curses.KEY_RIGHT: '\x1b[C',
    curses.KEY_LEFT: '\x1b[D',
    curses.KEY_HOME: '\x1b[H',
    curses.KEY_END: '\x1b[F',
    curses.KEY_DC: '\x1b[3~',
    curses.KEY_BACKSPACE: '\x7f',
    27: '\x1b', # Escape
}

def init_colors():
    # 1: Статус-бар (черный на белом)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # 2-9: Цвета текста (передний план)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_BLUE, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)
    curses.init_pair(7, curses.COLOR_CYAN, -1)
    curses.init_pair(8, curses.COLOR_WHITE, -1)
    curses.init_pair(9, curses.COLOR_BLACK, -1)
    # 10-17: Цвета фона (белый/черный текст на цветном фоне)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(14, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(15, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(16, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(17, curses.COLOR_BLACK, curses.COLOR_BLACK)

def get_color_attr(char):
    attr = 0
    if char.bold: attr |= curses.A_BOLD
    if char.underscore: attr |= curses.A_UNDERLINE
    if char.reverse: attr |= curses.A_REVERSE
    
    fg_map = {'black': 9, 'red': 2, 'green': 3, 'yellow': 4, 'blue': 5, 'magenta': 6, 'cyan': 7, 'white': 8}
    bg_map = {'red': 10, 'green': 11, 'yellow': 12, 'blue': 13, 'magenta': 14, 'cyan': 15, 'white': 16, 'black': 17}
    
    if char.fg in fg_map and char.bg == 'default':
        attr |= curses.color_pair(fg_map[char.fg])
    elif char.bg in bg_map and char.fg == 'default':
        attr |= curses.color_pair(bg_map[char.bg])
    elif char.fg in fg_map and char.bg in bg_map:
        attr |= curses.color_pair(bg_map[char.bg]) # Упрощенно используем цвет фона
        
    return attr

def run(stdscr):
    curses.curs_set(1)
    stdscr.nodelay(True)
    curses.start_color()
    curses.use_default_colors()
    init_colors()
    
    rows, cols = stdscr.getmaxyx()
    screen = pyte.Screen(cols, rows - 1)
    stream = pyte.Stream(screen)
    backend = YATBackend(cols, rows - 1)
    
    try:
        while backend.is_alive():
            data = backend.read()
            if data:
                stream.feed(data)
            
            stdscr.erase()
            
            # ИСПРАВЛЕНО: перебираем элементы словаря line.items(), а не enumerate(line)
            for y, line in screen.buffer.items():
                if y < rows - 1:
                    for x, char in line.items():
                        if x < cols:
                            try:
                                ch = char.data if char.data != '\x00' else ' '
                                attr = get_color_attr(char)
                                stdscr.addstr(y, x, ch, attr)
                            except curses.error:
                                pass
            
            # Курсор
            try:
                cy, cx = screen.cursor.y, screen.cursor.x
                if cy < rows - 1 and cx < cols:
                    stdscr.move(cy, cx)
            except curses.error:
                pass
                
            # Статус-бар
            status = f" YAT v0.1.0 | PowerShell | {cols}x{rows} [Ctrl+C to exit] "
            try:
                safe_status = status[:cols-1].ljust(cols - 1)
                stdscr.addstr(rows - 1, 0, safe_status, curses.color_pair(1))
            except curses.error:
                pass
            
            stdscr.refresh()
            
            # Ввод
            try:
                key = stdscr.getch()
                if key != -1:
                    if key == curses.KEY_RESIZE:
                        rows, cols = stdscr.getmaxyx()
                        screen.resize(cols, rows - 1)
                        backend.resize(cols, rows - 1)
                    elif key in SPECIAL_KEYS:
                        backend.write(SPECIAL_KEYS[key])
                    elif 0 <= key < 256:
                        backend.write(chr(key))
            except Exception:
                pass
                
            time.sleep(0.005)
            
    except KeyboardInterrupt:
        pass
    finally:
        backend.close()