# Typen - Terminal Speed Typing Test

A sleek, interactive terminal-based typing speed test application built with Python and `curses`.

---

## ⚡ Quick Install & Run (Zero Setup)

**Step 1:** Open any terminal and run **one** of these:

```bash
pip install git+https://github.com/Bhavish49/typer.git
```

> **If `pip` is not recognized**, try one of these instead:
> ```bash
> python -m pip install git+https://github.com/Bhavish49/typer.git
> ```
> ```bash
> py -m pip install git+https://github.com/Bhavish49/typer.git
> ```

**Step 2:** Launch the game from anywhere:

```bash
typen
```
*(or `speedtyper`)*

That's it! The typing test opens instantly.

**View your progress anytime:**
```bash
typen --stats
```

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

### 4. Progress Tracking & Personal Bests (Terminal-Native)
- **Automatic History Tracking**: Every completed test is recorded locally with speed, accuracy, duration, and errors.
- **Personal Best (PB) Alerts**: Celebratory highlight whenever you set a new WPM record in any difficulty and length mode.
- **Rolling Averages (Ao5 & Ao10)**: Standard speedcubing/typing benchmarks calculating your average of the last 5 and 10 tests.
- **In-Terminal Speed Trend Chart**: Visual ASCII trend graph and sparkline directly inside your terminal.
- **Dedicated Stats Dashboard**: Press `[S]` on the main menu to view all-time personal bests, total words typed, total practice time, and session history.
- **CLI Quick Stats**: Run `typen --stats` or `python typen.py --stats` for an instant terminal summary without opening the game.

### 5. Full Keyboard Controls
- Backspace support for corrections.
- Arrow keys / numbers for smooth 2-step menu selection.
- ESC to navigate back or exit anytime.
- Results screen displaying final WPM, accuracy, time taken, total characters typed, error count, and lifetime average comparison.

---

## 🎮 Controls

| Key | Action |
| --- | --- |
| `1` / `2` / `3` | Select difficulty or length directly |
| `S` | Open Progress & Stats dashboard from menu or results |
| `UP` / `DOWN` | Navigate menu options |
| `ENTER` | Confirm selection / Play again |
| `C` | Clear history (inside Stats Dashboard) |
| `BACKSPACE` | Delete previously typed character |
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
typen
# or:
python typen.py
```

> **Troubleshooting:** If `pip` or `python` is not recognized, you need to [add Python to your PATH](https://realpython.com/add-python-to-path/). On Windows, you can also try `py -m pip install -e .` and `py typen.py`.

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
