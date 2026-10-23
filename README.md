# Typer - Terminal Speed Typing Test

A sleek, interactive terminal-based typing speed test application built with Python and `curses`.

## 🚀 Features

- **3 Test Modes**:
  - **One Line**: Quick single-sentence sprint (~10–15 words).
  - **Stanza**: Medium test with poetic and prose stanzas (~35–50 words).
  - **One Page**: Comprehensive full-page typing challenge (~110–140 words).
- **Real-Time HUD**: Live tracking of **WPM** (Words Per Minute), **Accuracy (%)**, **Elapsed Time**, and **Progress (%)**.
- **Dynamic Word Wrapping & Auto-Scroll**: Long stanzas and multi-line paragraphs cleanly wrap by words and automatically scroll as you type to keep the active line in view.
- **Color Coded Feedback**:
  - Green for correctly typed characters.
  - Red for errors.
  - Underline indicator on the active character.
- **Full Key Support**: Backspace for editing, arrow keys for menu navigation, and ESC to return to the menu or exit anytime.
- **Results Summary**: Displays final WPM, accuracy, time taken, total characters typed, and error count.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Bhavish49/typer.git
   cd typer
   ```

2. **Install dependencies (Windows only):**
   Standard Unix systems include `curses` built into Python. On Windows, install `windows-curses`:
   ```bash
   pip install -r requirements.txt
   # or directly:
   pip install windows-curses
   ```

3. **Run the application:**
   ```bash
   python speed.py
   ```

---

## 🎮 Controls

| Key | Action |
| --- | --- |
| `1` / `2` / `3` | Directly select test mode from Menu |
| `UP` / `DOWN` | Navigate menu options |
| `ENTER` | Confirm selection / Play again |
| `BACKSPACE` | Delete previously typed character |
| `ESC` | Return to menu or exit |
| `M` | Return to menu from results screen |

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
