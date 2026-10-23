# Typer - Terminal Speed Typing Test

A sleek, interactive terminal-based typing speed test application built with Python and `curses`.

---

## ⚡ Quick Install & Run (Zero Setup)

You don't need to manually navigate folders or run scripts. You can install it directly as a system command using `pip`:

```bash
pip install git+https://github.com/Bhavish49/typer.git
```

Once installed, simply open any terminal (PowerShell, Command Prompt, macOS Terminal, Linux bash) and type:

```bash
typer
```
*(or `speedtyper`)*

The typing test will launch immediately!

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

### 4. Full Keyboard Controls
- Backspace support for corrections.
- Arrow keys / numbers for smooth 2-step menu selection.
- ESC to navigate back or exit anytime.
- Results screen displaying final WPM, accuracy, time taken, total characters typed, and error count.

---

## 🎮 Controls

| Key | Action |
| --- | --- |
| `1` / `2` / `3` | Select difficulty or length directly |
| `UP` / `DOWN` | Navigate menu options |
| `ENTER` | Confirm selection / Play again |
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
typer
# or:
python typer.py
# or:
python -m typer
```

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
