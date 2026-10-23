import curses
from curses import wrapper
import time
import random

# Curated sample texts categorized by length/mode
MODES = {
    "1": {
        "name": "One Line",
        "description": "Quick sprint (1 single sentence, ~10-15 words)",
        "texts": [
            "The quick brown fox jumps over the lazy dog near the quiet river bank.",
            "Programming is the art of telling another human what you want the computer to do.",
            "Consistency and daily practice are the secret keys to mastering typing speed and accuracy.",
            "Simplicity is a prerequisite for reliability, readability, and maintainable software design.",
            "Do not dwell in the past or dream of the future; concentrate your mind on the present moment.",
            "Success usually comes to those who are too focused and busy to be looking for it.",
            "In the middle of every difficulty lies a hidden opportunity to learn and grow.",
            "The only way to create truly great work is to love what you do every single day."
        ]
    },
    "2": {
        "name": "Stanza",
        "description": "Medium test (prose or poetry stanza, ~35-50 words)",
        "texts": [
            "Two roads diverged in a yellow wood, and sorry I could not travel both and be one traveler, long I stood and looked down one as far as I could to where it bent in the undergrowth.",
            "Hold fast to dreams, for if dreams die, life is a broken-winged bird that cannot fly. Hold fast to dreams, for when dreams go, life is a barren field frozen with white winter snow.",
            "The woods are lovely, dark and deep, but I have promises to keep, and miles to go before I sleep, and miles to go before I sleep under the quiet starry midnight sky.",
            "Do not go gentle into that good night, old age should burn and rave at close of day; rage, rage against the dying of the light, though wise men at their end know dark is right.",
            "I wandered lonely as a cloud that floats on high o'er vales and hills, when all at once I saw a crowd, a host of golden daffodils, beside the lake and beneath the trees."
        ]
    },
    "3": {
        "name": "One Page",
        "description": "Full page comprehensive test (~110-140 words)",
        "texts": [
            "Computers have transformed human civilization in ways our ancestors could never have imagined. From the mechanical gears of early calculating engines to the silicon microprocessors that power today's interconnected global network, each breakthrough has expanded the boundary of human capability. Touch typing emerged alongside the typewriter in the late nineteenth century as clerks discovered that assigning each finger to specific keys allowed seamless translation of thought into print. In modern software engineering, fluid typing speed coupled with unwavering accuracy removes the friction between conceptualizing an algorithm and realizing it in functioning code. Notice the rhythm of your keystrokes, maintain upright posture, and allow muscle memory to guide your fingers smoothly across the home row.",
            "The mystery of deep space has captured the curiosity of thinkers and dreamers across thousands of generations. Looking up at the shimmering expanse of stars on a clear night reminds us of our humble place in the cosmos, yet our scientific instruments have reached out to photograph the edges of observable space. Robotic rovers traverse the dusty red plains of Mars, automated probes voyage beyond the solar system into the cold interstellar void, and giant orbital telescopes capture the faint light emitted by newborn galaxies billions of years ago. Every line of code written to guide these spacecraft must be precise, reliable, and resilient against unexpected conditions. Developing discipline in your typing practice mirrors this standard of craftsmanship, building patience and precision with every sentence you complete.",
            "Learning any complex skill requires patience, intentional practice, and the willingness to embrace small incremental improvements over long stretches of time. When beginners sit before a keyboard, they often search for individual letters with their eyes, creating a bottleneck that hinders the natural flow of ideas. With persistent practice, however, the brain builds durable neural pathways connecting intended words directly to muscular movements of the hands. Eventually, the keyboard dissolves into an invisible medium, allowing writers, designers, and programmers to communicate with the digital world at the speed of thought. Celebrate every milestone in your journey, learn from typing errors, and keep striving toward effortless mastery."
        ]
    }
}

def layout_text(text, max_width):
    """
    Computes (row, col) coordinates for every character in text,
    wrapping words cleanly at max_width without cutting words in half.
    """
    words = text.split(' ')
    char_positions = []
    curr_row = 0
    curr_col = 0

    for w_idx, word in enumerate(words):
        word_with_space = word if w_idx == len(words) - 1 else word + " "
        # If adding this word exceeds max_width and we aren't at col 0, wrap to next line
        if curr_col + len(word) > max_width and curr_col > 0:
            curr_row += 1
            curr_col = 0

        for ch in word_with_space:
            char_positions.append((curr_row, curr_col, ch))
            curr_col += 1

    total_rows = curr_row + 1
    return char_positions, total_rows

def menu_screen(stdscr):
    """
    Menu to select between One Line, Stanza, or One Page test modes.
    Supports Up/Down arrows + Enter, or pressing 1, 2, 3 directly.
    """
    curses.curs_set(0)
    stdscr.nodelay(False)
    selected_idx = 0
    mode_keys = ["1", "2", "3"]

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "=== SPEED TYPING TEST ==="
        subtitle = "Select a Typing Mode to Begin:"

        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(max(0, h // 2 - 7), max(0, (w - len(title)) // 2), title)
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(max(0, h // 2 - 5), max(0, (w - len(subtitle)) // 2), subtitle)
        stdscr.attroff(curses.color_pair(4))

        # Render options
        for idx, key in enumerate(mode_keys):
            mode = MODES[key]
            item_text = f" [{key}] {mode['name']} - {mode['description']} "
            y = h // 2 - 2 + (idx * 2)
            x = max(2, (w - len(item_text)) // 2)

            if idx == selected_idx:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(4))

        # Help footer
        instructions = "Use [UP / DOWN] and [ENTER] to select, press [1-3], or [ESC] to exit"
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(max(0, h // 2 + 6), max(0, (w - len(instructions)) // 2), instructions)
        stdscr.attroff(curses.color_pair(3))

        stdscr.refresh()

        ch = stdscr.getch()

        if ch == 27:  # ESC
            return None
        elif ch in (curses.KEY_UP, ord('k'), ord('K')):
            selected_idx = (selected_idx - 1) % len(mode_keys)
        elif ch in (curses.KEY_DOWN, ord('j'), ord('J')):
            selected_idx = (selected_idx + 1) % len(mode_keys)
        elif ch in (10, 13, curses.KEY_ENTER):
            return mode_keys[selected_idx]
        elif ch in (ord('1'), ord('2'), ord('3')):
            return chr(ch)

def display_typing_arena(stdscr, mode_name, target_text, current_text, char_positions, total_rows, wpm, accuracy, elapsed):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Title & mode tag
    header = f" SPEED TYPING TEST  [{mode_name.upper()}] "
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(1, max(0, (w - len(header)) // 2), header)
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    # Progress %
    progress = (len(current_text) / len(target_text)) * 100 if target_text else 0.0

    # Live HUD Bar
    stats = f"  WPM: {wpm:3d}  |  Accuracy: {accuracy:5.1f}%  |  Time: {elapsed:4.1f}s  |  Progress: {progress:3.0f}%  |  [ESC: Menu]  "
    stdscr.attron(curses.color_pair(5))
    stdscr.addstr(3, max(0, (w - len(stats)) // 2), stats)
    stdscr.attroff(curses.color_pair(5))

    # Divider
    divider_len = min(w - 4, 82)
    divider = "-" * divider_len
    stdscr.attron(curses.color_pair(4))
    stdscr.addstr(4, max(0, (w - divider_len) // 2), divider)
    stdscr.attroff(curses.color_pair(4))

    # Text rendering area layout
    start_y = 6
    max_visible_rows = max(4, h - start_y - 3)
    max_width = min(80, max(20, w - 8))
    start_x = max(2, (w - max_width) // 2)

    # Current typing position row
    if len(current_text) < len(char_positions):
        current_cursor_row = char_positions[len(current_text)][0]
    else:
        current_cursor_row = char_positions[-1][0] if char_positions else 0

    # Scroll offset calculation to keep current typed line visible
    if total_rows > max_visible_rows:
        scroll_row = max(0, current_cursor_row - (max_visible_rows // 2))
        scroll_row = min(scroll_row, max(0, total_rows - max_visible_rows))
    else:
        scroll_row = 0

    # Render target text characters (dim / normal)
    typed_len = len(current_text)
    for idx, (r, c, target_ch) in enumerate(char_positions):
        screen_r = start_y + (r - scroll_row)
        if start_y <= screen_r < start_y + max_visible_rows:
            screen_c = start_x + c
            if screen_c < w - 1:
                if idx < typed_len:
                    # Already typed character: check if correct
                    user_ch = current_text[idx]
                    if user_ch == target_ch:
                        color = curses.color_pair(1)  # Green
                    else:
                        color = curses.color_pair(2)  # Red
                    stdscr.attron(color)
                    stdscr.addstr(screen_r, screen_c, user_ch)
                    stdscr.attroff(color)
                elif idx == typed_len:
                    # Current cursor character: underlined cyan
                    stdscr.attron(curses.color_pair(3) | curses.A_UNDERLINE | curses.A_BOLD)
                    stdscr.addstr(screen_r, screen_c, target_ch)
                    stdscr.attroff(curses.color_pair(3) | curses.A_UNDERLINE | curses.A_BOLD)
                else:
                    # Untyped character
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(screen_r, screen_c, target_ch)
                    stdscr.attroff(curses.color_pair(4))

    # Optional scroll indicator for longer pages
    if total_rows > max_visible_rows:
        indicator = f" [Lines {scroll_row + 1}-{min(total_rows, scroll_row + max_visible_rows)} of {total_rows}] "
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(h - 2, max(0, (w - len(indicator)) // 2), indicator)
        stdscr.attroff(curses.color_pair(4))

    stdscr.refresh()

def result_screen(stdscr, mode_name, wpm, accuracy, elapsed, total_chars, errors):
    stdscr.nodelay(False)
    curses.curs_set(0)
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    banner = "=== TEST COMPLETE! ==="
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(max(0, h // 2 - 6), max(0, (w - len(banner)) // 2), banner)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

    mode_info = f"Mode: {mode_name}"
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(max(0, h // 2 - 4), max(0, (w - len(mode_info)) // 2), mode_info)
    stdscr.attroff(curses.color_pair(3))

    lines = [
        f"Typing Speed:    {wpm} Words Per Minute (WPM)",
        f"Accuracy:        {accuracy:.1f}%",
        f"Time Elapsed:    {elapsed:.2f} seconds",
        f"Characters:      {total_chars} typed ({errors} errors)",
    ]

    for idx, line in enumerate(lines):
        y = h // 2 - 2 + idx
        x = max(0, (w - len(line)) // 2)
        stdscr.attron(curses.color_pair(5) if idx == 0 else curses.color_pair(4))
        stdscr.addstr(y, x, line)
        stdscr.attroff(curses.color_pair(5) if idx == 0 else curses.color_pair(4))

    prompt = "Press [ENTER] to play again, [M] for Menu, or [ESC] to quit"
    stdscr.attron(curses.A_BLINK | curses.color_pair(3))
    stdscr.addstr(max(0, h // 2 + 4), max(0, (w - len(prompt)) // 2), prompt)
    stdscr.attroff(curses.A_BLINK | curses.color_pair(3))

    stdscr.refresh()

    while True:
        ch = stdscr.getch()
        if ch == 27:  # ESC
            return "quit"
        elif ch in (ord('m'), ord('M')):
            return "menu"
        elif ch in (10, 13, curses.KEY_ENTER, ord(' ')):
            return "again"

def run_test(stdscr, mode_key):
    mode = MODES[mode_key]
    target_text = random.choice(mode["texts"])
    current_text = []

    h, w = stdscr.getmaxyx()
    max_width = min(80, max(20, w - 8))
    char_positions, total_rows = layout_text(target_text, max_width)

    start_time = None
    errors = 0
    total_keystrokes = 0

    stdscr.nodelay(True)

    while True:
        elapsed_time = max(time.time() - start_time, 0.1) if start_time else 0.0

        # Standard WPM: (characters / 5) / (minutes)
        if elapsed_time > 0 and start_time is not None:
            wpm = round((len(current_text) / 5) / (elapsed_time / 60))
        else:
            wpm = 0

        # Accuracy
        if total_keystrokes > 0:
            accuracy = max(0.0, ((total_keystrokes - errors) / total_keystrokes) * 100.0)
        else:
            accuracy = 100.0

        display_typing_arena(
            stdscr,
            mode["name"],
            target_text,
            current_text,
            char_positions,
            total_rows,
            wpm,
            accuracy,
            elapsed_time
        )

        # Check if completed
        if len(current_text) == len(target_text):
            action = result_screen(stdscr, mode["name"], wpm, accuracy, elapsed_time, len(current_text), errors)
            return action

        ch = stdscr.getch()

        if ch == -1:
            time.sleep(0.02)
            continue

        # Handle ESC key to return to menu
        if ch == 27:
            return "menu"

        # Handle terminal resize
        if ch == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            max_width = min(80, max(20, w - 8))
            char_positions, total_rows = layout_text(target_text, max_width)
            continue

        # Handle Backspace (works across Windows and Unix curses)
        if ch in (curses.KEY_BACKSPACE, 8, 127):
            if len(current_text) > 0:
                current_text.pop()
        elif 32 <= ch <= 126 and len(current_text) < len(target_text):
            if start_time is None:
                start_time = time.time()

            typed_char = chr(ch)
            expected_char = target_text[len(current_text)]
            if typed_char != expected_char:
                errors += 1
            total_keystrokes += 1
            current_text.append(typed_char)

def main(stdscr):
    # Initialize color pairs safely
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Correct characters
    curses.init_pair(2, curses.COLOR_RED, -1)     # Incorrect characters
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # Title & accents
    curses.init_pair(4, curses.COLOR_WHITE, -1)   # Standard text & hints
    curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Highlights & stats

    current_mode = None

    while True:
        if current_mode is None:
            current_mode = menu_screen(stdscr)
            if current_mode is None:
                break

        action = run_test(stdscr, current_mode)

        if action == "quit":
            break
        elif action == "menu":
            current_mode = None
        elif action == "again":
            # Replay with new text in the same mode
            continue

if __name__ == "__main__":
    wrapper(main)
