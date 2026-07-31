# BMI Calculator & Tracker

This is a Python GUI application built using `tkinter` that lets users calculate their Body Mass Index (BMI), classify it into standard health categories, save their history to a local database, and view their progress trend over time.

This project was built for the Oasis Infobyte Python Programming internship submission (Advanced tier).

## Features

- **BMI Calculation**: Computes BMI using weight (kg) and height (m) rounded to 2 decimal places.
- **Classification**: Groups BMI into Underweight (<18.5), Normal (18.5–24.9), Overweight (25–29.9), and Obese (>=30).
- **Color-Coded Visuals**: Colors category results to indicate status (green for Normal, orange for Underweight/Overweight, and red for Obese).
- **Database Storage**: Stores every record inside a local SQLite database file named `bmi_records.db`.
- **Multi-user Support**: Users can enter a custom name or pick an existing username to save and query their own history.
- **Progress Graph**: Uses matplotlib to show a line chart of a selected user's BMI changes over time.
- **Validation**: Checks inputs to prevent blank values, negative values, zeroes, or non-numeric inputs. Shows tkinter error popups.

## Tech Stack

- **Python 3.12**
- **Tkinter** (for desktop GUI layout)
- **SQLite3** (for local data storage)
- **Matplotlib** (for rendering charts)

## Database Schema

The historical records are stored in the `bmi_records` table within `bmi_records.db`. The table columns are:

| Column Name | Data Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key (auto-incrementing) |
| `name` | TEXT | Username entered by the user |
| `weight` | REAL | Entered weight in kilograms |
| `height` | REAL | Entered height in meters |
| `bmi` | REAL | Calculated BMI value (rounded to 2 decimal places) |
| `category` | TEXT | Health category classification |
| `timestamp` | TEXT | Date and time when calculation was made (`YYYY-MM-DD HH:MM:SS`) |

## Setup and Running

1. **Clone or download the project files** into a folder.
2. **Open a terminal/PowerShell** in the project directory.
3. **Set up a Python virtual environment** (recommended to keep things clean):
   ```bash
   python -m venv .venv
   ```
4. **Activate the environment**:
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
5. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Run the app**:
   ```bash
   python bmi_calculator.py
   ```

You can also run the automated tests using:
```bash
python -m unittest test_bmi.py
```
