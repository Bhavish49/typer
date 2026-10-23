import curses
from curses import wrapper
import time
import random
import sys
import stats_manager


def safe_addstr(stdscr, y, x, text, attr=0):
    """Safely adds string to curses window without crashing on terminal edge."""
    h, w = stdscr.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        available = w - x
        if y == h - 1:
            available -= 1
        if available > 0:
            try:
                stdscr.addstr(y, x, text[:available], attr)
            except curses.error:
                pass

# Curated typing texts categorized by Difficulty and Length
# Easy: Only normal words and basic spacing.
# Medium: Natural sentences with common punctuation (commas, periods, quotes, dashes, apostrophes, numbers).
# Hard: Meaningful, grammatically correct technical sentences with special characters (brackets, symbols, code syntax).
DATASET = {
    "easy": {
        "name": "Easy",
        "description": "Normal words only, simple and clean",
        "lengths": {
            "1": {
                "name": "One Line",
                "description": "Quick sprint (~10-15 words)",
                "texts": [
                    "the quick brown fox jumps over the lazy dog by the river bank",
                    "practice makes a person perfect in typing every single day",
                    "reading good books helps build a calm and creative mind",
                    "sunlight filtered gently through the tall green trees of the forest",
                    "early morning walks bring fresh energy and happiness to your life",
                    "consistency and patience are the true secrets of great success"
                ]
            },
            "2": {
                "name": "Stanza",
                "description": "Medium test (~35-50 words)",
                "texts": [
                    "walking through the quiet forest in the morning brings peaceful thoughts. the birds sing sweet songs from high branches while the cool breeze flows softly across the green grass.",
                    "hard work and dedication will always lead you toward your highest dreams. keep moving forward step by step and never lose faith in your own inner strength and wisdom.",
                    "the golden sun rises slowly over the distant blue hills. a new day begins with fresh hopes and quiet promises of simple joy and steady peaceful growth.",
                    "learning something new every day expands your horizon and sharpens your mind. always stay curious and embrace the small lessons that life offers you along the way."
                ]
            },
            "3": {
                "name": "One Page",
                "description": "Full page comprehensive test (~100-130 words)",
                "texts": [
                    "learning to type quickly and accurately is a wonderful skill that helps in school work and everyday life. when you practice every day with good posture your fingers naturally remember where every key is located. you do not need to look down at your hands because your mind and muscle memory work together in perfect harmony. take your time breathe deeply and focus on hitting each key smoothly without rushing. speed comes naturally when you focus on getting each word right first. with steady patience and daily effort you will soon notice great improvements in your typing confidence and flow across the keyboard."
                ]
            }
        }
    },
    "medium": {
        "name": "Medium",
        "description": "Everyday punctuation, quotes, numbers, and contractions",
        "lengths": {
            "1": {
                "name": "One Line",
                "description": "Quick sprint (~10-15 words)",
                "texts": [
                    "It's never too late to learn—especially when you're aiming for 100% accuracy!",
                    "She asked, \"Have you finished reading chapter 4?\" before leaving at 5:30 PM.",
                    "Success isn't just about speed; it's about making fewer mistakes along the way.",
                    "Over 75% of developers agree that fast typing saves hours of work each week.",
                    "Don't count the days; make the days count—that's the real secret to growth.",
                    "Life is 10% what happens to you and 90% how you react to it."
                ]
            },
            "2": {
                "name": "Stanza",
                "description": "Medium test (~35-50 words)",
                "texts": [
                    "Robert Frost wrote: \"Two roads diverged in a yellow wood, and sorry I could not travel both and be one traveler, long I stood and looked down one as far as I could.\" It's a reminder that our choices define our journey.",
                    "\"Life is what happens when you're busy making other plans,\" John Lennon once remarked in 1980. Every second counts, so don't let small distractions steal your focus from what truly matters today.",
                    "In 1969, Apollo 11 landed on the Moon; Neil Armstrong said, \"That's one small step for man, one giant leap for mankind.\" It took over 400,000 engineers and scientists to turn that dream into reality."
                ]
            },
            "3": {
                "name": "One Page",
                "description": "Full page comprehensive test (~110-140 words)",
                "texts": [
                    "Modern software development is as much about clear communication as it is about writing code. In 1995, Java introduced the slogan \"Write once, run anywhere,\" which shaped how cross-platform computing evolved over the next 30 years. Today, teams collaborate across different time zones—from San Francisco (PST) to Tokyo (JST)—using tools like Git, Slack, and cloud platforms. Writing concise comments, well-structured documentation, and descriptive commit messages prevents costly misunderstandings. When you type with speed and precision, you reduce the gap between thinking through a complex problem and expressing its solution. Remember: clarity is always king; speed is merely its faithful servant."
                ]
            }
        }
    },
    "hard": {
        "name": "Hard",
        "description": "Special characters, brackets, symbols, and technical syntax",
        "lengths": {
            "1": {
                "name": "One Line",
                "description": "Quick sprint (~10-15 words)",
                "texts": [
                    "if (user.get_wpm() >= 80 && accuracy > 95.5%) { return Status::EXCELLENT; }",
                    "const config = { host: '127.0.0.1', port: 8080, ssl: true, timeout: 3000 };",
                    "Run `git clone https://github.com/user/repo.git --branch v2.1.0` to start!",
                    "Calculate: (x_val * 100.0) / (total_count - error_sum) >= target_ratio [OK]",
                    "SELECT user_id, email FROM accounts WHERE status = 'ACTIVE' AND score >= 90;",
                    "curl -X POST https://api.service.io/v1/auth -H 'Content-Type: application/json'"
                ]
            },
            "2": {
                "name": "Stanza",
                "description": "Medium test (~35-50 words)",
                "texts": [
                    "In Python, decorators wrap functions gracefully: `@benchmark(runs=100) def compute_hash(data: bytes) -> str:` computes SHA-256 hashes inside a `try/except (ValueError, KeyError)` block, returning `{'status': 200, 'hash': result}`.",
                    "When optimizing algorithms, O(n*log(n)) time complexity is vastly superior to O(n^2). Consider a hash table lookup: with O(1) amortized cost, keys in `table['user_id']` resolve in < 5ms even when size > 1,000,000 items!",
                    "To build the Docker container: run `docker build -t app:v1.0.4 . --build-arg ENV=production` & ensure ports [80:8080, 443:8443] are forwarded through the firewall (iptables -A INPUT -p tcp --dport 443 -j ACCEPT)."
                ]
            },
            "3": {
                "name": "One Page",
                "description": "Full page comprehensive test (~110-140 words)",
                "texts": [
                    "Building robust distributed systems requires careful handling of edge cases, race conditions, and network latency. Consider a microservice architecture where Service-A communicates with Service-B over gRPC: `rpc FetchUserProfile(UserRequest) returns (UserResponse) { option (auth_required) = true; }`. If the request fails with status code `503_UNAVAILABLE`, an exponential backoff policy kicks in: `retry_delay = min(max_backoff, base_delay * (2 ** attempt)) + random.uniform(0.1, 0.5)`. Memory management is equally crucial: buffer sizes must stay capped at `<= 64MB` to prevent out-of-memory errors (`SIGKILL: exit 137`). Developers who master these technical patterns write resilient code with high test coverage (`pytest --cov=src --cov-report=html`), ensuring 99.99% uptime across production clusters."
                ]
            }
        }
    }
}

def layout_text(text, max_width):
    """
    Computes (row, col) coordinates for each character in text,
    wrapping words cleanly at max_width without truncating words.
    """
    words = text.split(' ')
    char_positions = []
    curr_row = 0
    curr_col = 0

    for w_idx, word in enumerate(words):
        word_with_space = word if w_idx == len(words) - 1 else word + " "
        if curr_col + len(word) > max_width and curr_col > 0:
            curr_row += 1
            curr_col = 0

        for ch in word_with_space:
            char_positions.append((curr_row, curr_col, ch))
            curr_col += 1

    total_rows = curr_row + 1
    return char_positions, total_rows

def difficulty_menu(stdscr):
    """
    Step 1: Select Difficulty Level (Easy, Medium, Hard) or View Stats.
    """
    curses.curs_set(0)
    stdscr.nodelay(False)
    diff_keys = ["easy", "medium", "hard", "stats"]
    selected_idx = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "=== SPEED TYPING TEST ==="
        subtitle = "Select an option to begin:"

        safe_addstr(stdscr, max(0, h // 2 - 8), max(0, (w - len(title)) // 2), title, curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(stdscr, max(0, h // 2 - 6), max(0, (w - len(subtitle)) // 2), subtitle, curses.color_pair(4))

        menu_items = [
            ("1", "EASY", "Normal words only, simple and clean"),
            ("2", "MEDIUM", "Everyday punctuation, quotes, numbers, contractions"),
            ("3", "HARD", "Special characters, brackets, symbols, code syntax"),
            ("S", "STATS & PROGRESS", "View speed trend chart, personal bests & history"),
        ]

        for idx, (hotkey, name, desc) in enumerate(menu_items):
            item_text = f" [{hotkey}] {name} - {desc} "
            y = h // 2 - 3 + (idx * 2)
            x = max(2, (w - len(item_text)) // 2)

            if idx == selected_idx:
                safe_addstr(stdscr, y, x, item_text, curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            else:
                safe_addstr(stdscr, y, x, item_text, curses.color_pair(4))

        instructions = "Use [UP / DOWN] & [ENTER], press [1-3, S], or [ESC] to exit"
        safe_addstr(stdscr, max(0, h // 2 + 7), max(0, (w - len(instructions)) // 2), instructions, curses.color_pair(3))

        stdscr.refresh()

        ch = stdscr.getch()

        if ch == 27:  # ESC
            return None
        elif ch in (curses.KEY_UP, ord('k'), ord('K')):
            selected_idx = (selected_idx - 1) % len(diff_keys)
        elif ch in (curses.KEY_DOWN, ord('j'), ord('J')):
            selected_idx = (selected_idx + 1) % len(diff_keys)
        elif ch in (10, 13, curses.KEY_ENTER):
            return diff_keys[selected_idx]
        elif ch in (ord('1'), ord('2'), ord('3')):
            return diff_keys[ch - ord('1')]
        elif ch in (ord('s'), ord('S')):
            return "stats"

def stats_dashboard(stdscr):
    """
    Dedicated curses screen for viewing lifetime stats, rolling averages,
    ASCII speed trend chart, and recent sessions.
    """
    curses.curs_set(0)
    stdscr.nodelay(False)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        data = stats_manager.load_history()
        summary = data.get("summary", {})
        sessions = data.get("sessions", [])
        metrics = stats_manager.compute_metrics(sessions)

        title = "=== TYPING STATS & PROGRESS DASHBOARD ==="
        safe_addstr(stdscr, 1, max(0, (w - len(title)) // 2), title, curses.color_pair(3) | curses.A_BOLD)

        # Overview cards / lines
        total_sec = summary.get("total_time_seconds", 0.0)
        mins = int(total_sec // 60)
        secs = int(total_sec % 60)

        ao5_str = f"{metrics['ao5']} WPM" if metrics['ao5'] is not None else "N/A (need 5)"
        ao10_str = f"{metrics['ao10']} WPM" if metrics['ao10'] is not None else "N/A (need 10)"

        line1 = f"Tests: {metrics['total_tests']}   |   Words: {summary.get('total_words', 0)}   |   Practice Time: {mins}m {secs}s"
        line2 = f"Best Speed: {metrics['best_wpm']} WPM   |   Avg Speed: {metrics['avg_wpm']} WPM   |   Best Acc: {metrics['best_acc']:.1f}%"
        line3 = f"Rolling Averages:  Ao5 = {ao5_str}   |   Ao10 = {ao10_str}"

        safe_addstr(stdscr, 3, max(2, (w - len(line1)) // 2), line1, curses.color_pair(4))
        safe_addstr(stdscr, 4, max(2, (w - len(line2)) // 2), line2, curses.color_pair(5) | curses.A_BOLD)
        safe_addstr(stdscr, 5, max(2, (w - len(line3)) // 2), line3, curses.color_pair(3))

        # Speed Trend Chart
        chart_header = "-- Recent Speed Trend --"
        safe_addstr(stdscr, 7, max(2, (w - len(chart_header)) // 2), chart_header, curses.color_pair(4) | curses.A_UNDERLINE)

        chart_max_pts = min(12, max(4, (w - 18) // 3))
        chart_lines = stats_manager.generate_ascii_chart(sessions, max_points=chart_max_pts, height=5)
        for c_idx, c_line in enumerate(chart_lines):
            safe_addstr(stdscr, 8 + c_idx, max(2, (w - len(c_line)) // 2), c_line, curses.color_pair(4))

        chart_bottom_y = 8 + len(chart_lines)

        # Recent sessions table (last 4)
        if h > chart_bottom_y + 8:
            table_header = "-- Last Sessions --"
            safe_addstr(stdscr, chart_bottom_y + 1, max(2, (w - len(table_header)) // 2), table_header, curses.color_pair(4) | curses.A_UNDERLINE)

            cols_header = " Date & Time       Mode               WPM      Acc %    Time     PB "
            safe_addstr(stdscr, chart_bottom_y + 2, max(2, (w - len(cols_header)) // 2), cols_header, curses.color_pair(5) | curses.A_BOLD)

            max_show = min(4, h - chart_bottom_y - 5)
            for idx, s in enumerate(sessions[-max_show:]):
                mode = f"{s.get('diff_name', '')[:6]} ({s.get('length_name', '')[:6]})"
                pb_tag = "[PB]" if s.get("is_pb") else "    "
                row_str = f" {s.get('timestamp', ''):<17} {mode:<18} {s.get('wpm', 0):<8} {s.get('accuracy', 0.0):.1f}%    {s.get('elapsed_seconds', 0.0):.1f}s    {pb_tag} "
                safe_addstr(stdscr, chart_bottom_y + 3 + idx, max(2, (w - len(row_str)) // 2), row_str, curses.color_pair(4))

        # Footer controls
        prompt = "[C] Clear History   |   [ESC / ENTER / B] Back to Menu"
        safe_addstr(stdscr, h - 2, max(0, (w - len(prompt)) // 2), prompt, curses.color_pair(3) | curses.A_BOLD)

        stdscr.refresh()

        ch = stdscr.getch()

        if ch in (27, 10, 13, curses.KEY_ENTER, ord('b'), ord('B'), ord('q'), ord('Q')):
            return
        elif ch in (ord('c'), ord('C')):
            confirm_msg = "Are you sure you want to clear all history? [Y / N]: "
            safe_addstr(stdscr, h - 2, max(0, (w - len(confirm_msg)) // 2), confirm_msg, curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            conf_ch = stdscr.getch()
            if conf_ch in (ord('y'), ord('Y')):
                stats_manager.clear_history()

def length_menu(stdscr, diff_key):
    """
    Step 2: Select Text Length (One Line, Stanza, One Page).
    """
    curses.curs_set(0)
    stdscr.nodelay(False)
    diff_name = DATASET[diff_key]["name"]
    lengths = DATASET[diff_key]["lengths"]
    length_keys = ["1", "2", "3"]
    selected_idx = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = f"=== SPEED TYPING TEST [{diff_name.upper()}] ==="
        subtitle = "STEP 2: Select Text Length"

        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(max(0, h // 2 - 7), max(0, (w - len(title)) // 2), title)
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(max(0, h // 2 - 5), max(0, (w - len(subtitle)) // 2), subtitle)
        stdscr.attroff(curses.color_pair(4))

        for idx, key in enumerate(length_keys):
            info = lengths[key]
            item_text = f" [{key}] {info['name']} - {info['description']} "
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

        instructions = "Use [UP / DOWN] & [ENTER], press [1-3], or [ESC] to go back"
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(max(0, h // 2 + 6), max(0, (w - len(instructions)) // 2), instructions)
        stdscr.attroff(curses.color_pair(3))

        stdscr.refresh()

        ch = stdscr.getch()

        if ch == 27:  # ESC goes back
            return None
        elif ch in (curses.KEY_UP, ord('k'), ord('K')):
            selected_idx = (selected_idx - 1) % len(length_keys)
        elif ch in (curses.KEY_DOWN, ord('j'), ord('J')):
            selected_idx = (selected_idx + 1) % len(length_keys)
        elif ch in (10, 13, curses.KEY_ENTER):
            return length_keys[selected_idx]
        elif ch in (ord('1'), ord('2'), ord('3')):
            return chr(ch)

def display_typing_arena(stdscr, diff_name, length_name, target_text, current_text, char_positions, total_rows, wpm, accuracy, elapsed):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Header with current configuration
    header = f" SPEED TYPING TEST  [{diff_name.upper()} | {length_name.upper()}] "
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

    # Text rendering area
    start_y = 6
    max_visible_rows = max(4, h - start_y - 3)
    max_width = min(80, max(20, w - 8))
    start_x = max(2, (w - max_width) // 2)

    # Current typing position row
    if len(current_text) < len(char_positions):
        current_cursor_row = char_positions[len(current_text)][0]
    else:
        current_cursor_row = char_positions[-1][0] if char_positions else 0

    # Auto-scroll offset
    if total_rows > max_visible_rows:
        scroll_row = max(0, current_cursor_row - (max_visible_rows // 2))
        scroll_row = min(scroll_row, max(0, total_rows - max_visible_rows))
    else:
        scroll_row = 0

    # Render characters
    typed_len = len(current_text)
    for idx, (r, c, target_ch) in enumerate(char_positions):
        screen_r = start_y + (r - scroll_row)
        if start_y <= screen_r < start_y + max_visible_rows:
            screen_c = start_x + c
            if screen_c < w - 1:
                if idx < typed_len:
                    user_ch = current_text[idx]
                    if user_ch == target_ch:
                        color = curses.color_pair(1)  # Green
                    else:
                        color = curses.color_pair(2)  # Red
                    stdscr.attron(color)
                    stdscr.addstr(screen_r, screen_c, user_ch)
                    stdscr.attroff(color)
                elif idx == typed_len:
                    stdscr.attron(curses.color_pair(3) | curses.A_UNDERLINE | curses.A_BOLD)
                    stdscr.addstr(screen_r, screen_c, target_ch)
                    stdscr.attroff(curses.color_pair(3) | curses.A_UNDERLINE | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(screen_r, screen_c, target_ch)
                    stdscr.attroff(curses.color_pair(4))

    if total_rows > max_visible_rows:
        indicator = f" [Lines {scroll_row + 1}-{min(total_rows, scroll_row + max_visible_rows)} of {total_rows}] "
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(h - 2, max(0, (w - len(indicator)) // 2), indicator)
        stdscr.attroff(curses.color_pair(4))

    stdscr.refresh()

def result_screen(stdscr, diff_key, diff_name, length_key, length_name, wpm, accuracy, elapsed, total_chars, errors):
    stdscr.nodelay(False)
    curses.curs_set(0)
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Record session & get stats comparison
    stats_info = stats_manager.record_session(
        diff_key, diff_name, length_key, length_name, wpm, accuracy, elapsed, total_chars, errors
    )

    y_offset = max(1, h // 2 - 8)

    # Personal best banner
    if stats_info.get("is_category_pb"):
        prev_best = stats_info.get("prev_category_best", 0)
        pb_banner = f"*** NEW PERSONAL BEST! (Previous: {prev_best} WPM -> Now: {wpm} WPM) ***"
        safe_addstr(stdscr, y_offset, max(0, (w - len(pb_banner)) // 2), pb_banner, curses.color_pair(5) | curses.A_BOLD)
        y_offset += 2

    banner = "=== TEST COMPLETE! ==="
    safe_addstr(stdscr, y_offset, max(0, (w - len(banner)) // 2), banner, curses.color_pair(1) | curses.A_BOLD)
    y_offset += 2

    config_info = f"Difficulty: {diff_name}   |   Length: {length_name}"
    safe_addstr(stdscr, y_offset, max(0, (w - len(config_info)) // 2), config_info, curses.color_pair(3))
    y_offset += 2

    lifetime_avg = stats_info.get("lifetime_avg_wpm", float(wpm))
    diff_from_avg = stats_info.get("wpm_diff_from_avg", 0.0)
    avg_comparison = f"({diff_from_avg:+.1f} vs lifetime avg of {lifetime_avg:.1f} WPM)"

    lines = [
        f"Typing Speed:    {wpm} Words Per Minute (WPM) {avg_comparison}",
        f"Accuracy:        {accuracy:.1f}%",
        f"Time Elapsed:    {elapsed:.2f} seconds",
        f"Characters:      {total_chars} typed ({errors} errors)",
    ]

    for idx, line in enumerate(lines):
        y = y_offset + idx
        x = max(0, (w - len(line)) // 2)
        attr = curses.color_pair(5) | curses.A_BOLD if idx == 0 else curses.color_pair(4)
        safe_addstr(stdscr, y, x, line, attr)

    prompt = "Press [ENTER] to play again, [M] for Menu, [S] for Stats, or [ESC] to quit"
    safe_addstr(stdscr, y_offset + len(lines) + 2, max(0, (w - len(prompt)) // 2), prompt, curses.A_BLINK | curses.color_pair(3))

    stdscr.refresh()

    while True:
        ch = stdscr.getch()
        if ch == 27:  # ESC
            return "quit"
        elif ch in (ord('m'), ord('M')):
            return "menu"
        elif ch in (ord('s'), ord('S')):
            stats_dashboard(stdscr)
            return "menu"
        elif ch in (10, 13, curses.KEY_ENTER, ord(' ')):
            return "again"

def run_test(stdscr, diff_key, length_key):
    diff_name = DATASET[diff_key]["name"]
    length_info = DATASET[diff_key]["lengths"][length_key]
    length_name = length_info["name"]
    target_text = random.choice(length_info["texts"])
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

        if elapsed_time > 0 and start_time is not None:
            wpm = round((len(current_text) / 5) / (elapsed_time / 60))
        else:
            wpm = 0

        if total_keystrokes > 0:
            accuracy = max(0.0, ((total_keystrokes - errors) / total_keystrokes) * 100.0)
        else:
            accuracy = 100.0

        display_typing_arena(
            stdscr,
            diff_name,
            length_name,
            target_text,
            current_text,
            char_positions,
            total_rows,
            wpm,
            accuracy,
            elapsed_time
        )

        if len(current_text) == len(target_text):
            action = result_screen(
                stdscr,
                diff_key,
                diff_name,
                length_key,
                length_name,
                wpm,
                accuracy,
                elapsed_time,
                len(current_text),
                errors
            )
            return action

        ch = stdscr.getch()

        if ch == -1:
            time.sleep(0.02)
            continue

        if ch == 27:  # ESC to return to menu
            return "menu"

        if ch == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            max_width = min(80, max(20, w - 8))
            char_positions, total_rows = layout_text(target_text, max_width)
            continue

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
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Correct character
    curses.init_pair(2, curses.COLOR_RED, -1)     # Incorrect character
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # Title & highlights
    curses.init_pair(4, curses.COLOR_WHITE, -1)   # Target text & general UI
    curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Selected / Stats

    diff_choice = None
    length_choice = None

    while True:
        # Step 1: Select Difficulty or Stats
        if diff_choice is None:
            diff_choice = difficulty_menu(stdscr)
            if diff_choice is None:
                break  # Exit
            if diff_choice == "stats":
                stats_dashboard(stdscr)
                diff_choice = None
                continue

        # Step 2: Select Length
        if length_choice is None:
            length_choice = length_menu(stdscr, diff_choice)
            if length_choice is None:
                diff_choice = None  # Go back to difficulty selection
                continue

        # Run typing test
        action = run_test(stdscr, diff_choice, length_choice)

        if action == "quit":
            break
        elif action == "menu":
            length_choice = None  # Return to length menu (or ESC to go back to difficulty)
        elif action == "again":
            continue

def cli():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--stats", "-s", "stats"):
        stats_manager.print_cli_stats()
        return

    try:
        wrapper(main)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    cli()
