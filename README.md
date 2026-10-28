# Typer - Terminal Speed Typing Test

A sleek, interactive terminal-based typing speed test application built with Python and `curses`.

---

## ⚡ Quick Install & Run (Zero Setup)

**Step 1:** Open any terminal and run **one** of these:

```bash
pip install git+https://github.com/Bhavish49/typer.git
```

> ⚠️ **Important:** Always use the full command above. Do **NOT** run bare `pip install typer` (which downloads an unrelated Python CLI library from PyPI).

> **If `pip` is not recognized**, try one of these instead:
> ```bash
> python -m pip install git+https://github.com/Bhavish49/typer.git
> ```
> ```bash
> py -m pip install git+https://github.com/Bhavish49/typer.git
> ```

**Step 2:** Launch the game from anywhere:

```bash
typer
```
*(or `speedtyper`)*

Login to your profile, and the typing test and private stats dashboard open instantly.

---

## 🖱️ Windows 1-Click Launch (No Commands Needed)

If you downloaded or cloned this folder, simply **double-click** [`run.bat`](run.bat).
It automatically checks dependencies and opens the game directly.

---

## 🚀 Features

### 1. Difficulty Levels
- **Easy**: Normal words only, clean and lowercase/simple phrasing with no tricky symbols or special characters.
- **Medium**: Natural everyday sentences with common punctuation (commas, quotes `""`, apostrophes `'`, dashes `-`, colons `:`, and numbers).
- **Hard**: High-challenge, grammatically sound technical sentences with special characters (brackets `()`, `[]`, `{}`, symbols `@`, `$`, `%`, `&`, `*`, `_`, `=`, `/`, `<>`, and code syntax).

### 2. Text Length Options
For every difficulty level, you can choose the text length:
- **One Line**: Quick single-sentence sprint (~10–15 words).
- **Stanza**: Medium test with stanzas / short paragraphs (~35–50 words).
- **One Page**: Comprehensive full-page typing challenge (~100–140 words).

### 3. Real-Time HUD & Visuals
- Live **WPM** (Words Per Minute), **Accuracy (%)**, **Elapsed Time**, and **Progress (%)**.
- **Dynamic Word Wrapping & Auto-Scroll**: Multi-line paragraphs cleanly wrap by whole words and automatically scroll as you type to keep the active line visible.
- **Color-Coded Character Feedback**:
  - Green for correctly typed characters.
  - Red for errors.
  - Underline indicator on the active cursor character.

### 4. 👤 Multi-User Profiles & Demo Mode
- **Multi-User on Same Computer**: When the app opens, choose **[1] Login**, **[2] Create Profile**, or **[3] Demo Mode**.
- **Password Protected**: Simple, salted SHA-256 password hashing keeps individual stats separate and private.
- **Demo / Guest Mode**: Instant practice with live HUD and results without saving any stats to the database.
- **Switch Profiles Anytime**: Press `[U]` from the main menu or stats dashboard to switch users instantly.

### 5. 🎯 Weak Keys & Stumble Analysis (Learn & Improve)
- **Automatic Mistake Tracking**: Tracks every character you stumble or make errors on during tests.
- **Top 5 Weakest Keys**: Analyzes your error patterns and ranks the top 5 keys with total error counts and percentages.
- **Actionable Advice**: Highlights exactly which keys need practice so you can slow down on them and boost accuracy.

### 6. 📊 Progress Tracking & Personal Bests (Terminal-Native)
- **Automatic History Tracking**: Every completed test is recorded locally under your profile with speed, accuracy, duration, and errors.
- **Personal Best (PB) Alerts**: Celebratory highlight whenever you set a new WPM record in any difficulty and length mode.
- **Rolling Averages (Ao5 & Ao10)**: Standard speedcubing/typing benchmarks calculating your average of the last 5 and 10 tests.
- **In-Terminal Speed Trend Chart**: Visual ASCII trend graph directly inside your dashboard.
- **Dedicated Stats Dashboard**: Press `[S]` on the menu after login to view your personal bests, top weak keys, total practice time, and session history.

### 7. Full Keyboard Controls
- Backspace support for corrections.
- Arrow keys / numbers for smooth menu selection.
- ESC to navigate back or exit anytime.
- Results screen displaying final WPM, accuracy, time taken, total characters typed, error count, session stumbles, and top weak keys.

---

## 🎮 Controls

| Key | Action |
| --- | --- |
| `1` / `2` / `3` | Select difficulty or length directly |
| `S` | Open Progress & Stats dashboard from menu or results |
| `UP` / `DOWN` | Navigate menu options |
| `ENTER` | Confirm selection / Play again |
| `C` | Clear history (inside Stats Dashboard) |
| `ESC` | Go back to previous step / Return to menu / Exit |
| `M` | Return to menu from results screen |

---

## 🛠️ Manual Clone / Developer Setup

If you prefer to clone and develop locally:

```bash
git clone https://github.com/Bhavish49/typer.git
cd typer

# Install in editable mode
pip install -e .

# Run via command or script
typer
# or:
python typer.py
```

> **Troubleshooting:** If `pip` or `python` is not recognized, you need to [add Python to your PATH](https://realpython.com/add-python-to-path/). On Windows, you can also try `py -m pip install -e .` and `py typer.py`.

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
