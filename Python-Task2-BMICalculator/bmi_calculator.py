import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import os
import sys

# Point Tcl/Tk environment variables to virtual env if present, 
# to fix TclError about init.tcl not found
base_dir = os.path.dirname(os.path.abspath(__file__))
venv_tcl = os.path.join(base_dir, ".venv", "Lib", "site-packages", "tcl")
if os.path.exists(venv_tcl):
    os.environ["TCL_LIBRARY"] = os.path.join(venv_tcl, "tcl8.6")
    os.environ["TK_LIBRARY"] = os.path.join(venv_tcl, "tk8.6")

# Database helper functions

def init_db():
    # Setup SQLite table if it doesn't exist yet
    conn = sqlite3.connect("bmi_records.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_record(name, weight, height, bmi, category):
    # Save a run to the db with current timestamp
    conn = sqlite3.connect("bmi_records.db")
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO bmi_records (name, weight, height, bmi, category, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name.strip(), weight, height, bmi, category, now_str))
    conn.commit()
    conn.close()

def get_user_history(name):
    # Fetch all records for this user, sorted by time
    conn = sqlite3.connect("bmi_records.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bmi, timestamp, weight, height, category 
        FROM bmi_records 
        WHERE name = ? 
        ORDER BY timestamp ASC
    """, (name.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_unique_users():
    # Helper to populate the combobox dropdown
    conn = sqlite3.connect("bmi_records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM bmi_records ORDER BY name ASC")
    # flatten list of tuples
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# Core calculation and classification logic

def calc_bmi(weight, height):
    # BMI formula: weight (kg) / height^2 (m)
    # rounding to 2 decimals so it doesn't look messy
    return round(weight / (height ** 2), 2)

def get_category(bmi):
    # Classify BMI and get styling color
    # green for normal, orange for underweight/overweight, red for obese
    if bmi < 18.5:
        return "Underweight", "#d35400"  # orange
    elif 18.5 <= bmi < 25:
        return "Normal", "#27ae60"       # green
    elif 25 <= bmi < 30:
        return "Overweight", "#e67e22"   # orange
    else:
        return "Obese", "#c0392b"        # red


class BMICalculatorApp:
    def __init__(self, root):
        # Import tkinter locally so we can run unit tests on headless environments
        import tkinter as tk
        from tkinter import ttk, messagebox
        self.tk = tk
        self.ttk = ttk
        self.messagebox = messagebox
        
        self.root = root
        self.root.title("BMI Tracker")
        self.root.geometry("450x480")
        self.root.resizable(False, False)
        
        # Configure grid weight so it centers nicely
        self.root.columnconfigure(0, weight=1)
        
        # Initialize DB
        init_db()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure layout and styling
        style = self.ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), foreground="#2c3e50")
        
        # Main container frame
        main_frame = self.ttk.Frame(self.root, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        
        # Header Label
        header = self.ttk.Label(main_frame, text="BMI Calculator & Tracker", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input Frame
        input_lf = self.ttk.LabelFrame(main_frame, text=" User Details ", padding=15)
        input_lf.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        input_lf.columnconfigure(1, weight=1)
        
        # Name Input
        self.ttk.Label(input_lf, text="User Name:").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.name_combo = self.ttk.Combobox(input_lf)
        self.name_combo.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Weight Input
        self.ttk.Label(input_lf, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        self.weight_entry = self.ttk.Entry(input_lf)
        self.weight_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Height Input
        self.ttk.Label(input_lf, text="Height (m):").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
        self.height_entry = self.ttk.Entry(input_lf)
        self.height_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Buttons Frame
        btn_frame = self.ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        calc_btn = self.ttk.Button(btn_frame, text="Calculate BMI", command=self.handle_calculate)
        calc_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        clear_btn = self.ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields)
        clear_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Results Frame
        result_lf = self.ttk.LabelFrame(main_frame, text=" Results ", padding=15)
        result_lf.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        result_lf.columnconfigure(0, weight=1)
        result_lf.columnconfigure(1, weight=1)
        
        self.ttk.Label(result_lf, text="Calculated BMI:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="e", padx=(0, 10), pady=5)
        self.bmi_val_label = self.ttk.Label(result_lf, text="--", font=("Arial", 12, "bold"), foreground="#2c3e50")
        self.bmi_val_label.grid(row=0, column=1, sticky="w", pady=5)
        
        self.ttk.Label(result_lf, text="Category:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)
        self.category_label = self.ttk.Label(result_lf, text="--", font=("Arial", 12, "bold"))
        self.category_label.grid(row=1, column=1, sticky="w", pady=5)
        
        # Trend Graph Button
        self.trend_btn = self.ttk.Button(main_frame, text="Show Trend Graph", command=self.show_trend)
        self.trend_btn.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        
        # TODO: maybe add BMI category tooltip later
        
        # Load user list to dropdown
        self.refresh_users()
        
    def refresh_users(self):
        # Refresh user list in combobox
        users = get_unique_users()
        self.name_combo['values'] = users
        if users:
            # Default to first user if combobox is empty
            if not self.name_combo.get():
                self.name_combo.set(users[0])
                
    def clear_fields(self):
        # Reset text entries and results
        self.weight_entry.delete(0, self.tk.END)
        self.height_entry.delete(0, self.tk.END)
        self.bmi_val_label.config(text="--")
        self.category_label.config(text="--", foreground="black")
        
    def handle_calculate(self):
        name = self.name_combo.get().strip()
        if not name:
            self.messagebox.showerror("Validation Error", "Please enter or select a user name.")
            return
            
        try:
            w_text = self.weight_entry.get().strip()
            h_text = self.height_entry.get().strip()
            
            if not w_text or not h_text:
                self.messagebox.showerror("Validation Error", "Weight and height fields cannot be empty.")
                return
                
            weight = float(w_text)
            height = float(h_text)
            
            if weight <= 0 or height <= 0:
                self.messagebox.showerror("Validation Error", "Weight and height must be positive numbers greater than zero.")
                return
                
        except ValueError:
            self.messagebox.showerror("Validation Error", "Please enter valid numeric values for weight and height.")
            return
            
        # Calculation and styling
        bmi = calc_bmi(weight, height)
        category, color = get_category(bmi)
        
        # Save to SQLite database
        save_record(name, weight, height, bmi, category)
        
        # Update labels with results
        self.bmi_val_label.config(text=f"{bmi}")
        self.category_label.config(text=category, foreground=color)
        
        # Reload combobox values to include the new name if it wasn't there
        self.refresh_users()
        self.name_combo.set(name)
        
    def show_trend(self):
        name = self.name_combo.get().strip()
        if not name:
            self.messagebox.showerror("Error", "Please enter or select a user name first.")
            return
            
        history = get_user_history(name)
        if not history:
            self.messagebox.showinfo("No History", f"No records found for '{name}'. Record at least one BMI calculation first.")
            return
            
        # Extract data for plotting
        bmis = [row[0] for row in history]
        timestamps = [row[1] for row in history]
        
        # Parse timestamp string for cleaner labels on X-axis
        formatted_dates = []
        for ts in timestamps:
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                formatted_dates.append(dt.strftime("%b %d\n%H:%M"))
            except ValueError:
                formatted_dates.append(ts)
                
        # Matplotlib plotting
        plt.figure(figsize=(7, 4.5))
        plt.plot(formatted_dates, bmis, marker='o', color='#2c3e50', linewidth=2, label='BMI')
        
        # Reference line thresholds
        plt.axhline(y=18.5, color='#d35400', linestyle='--', alpha=0.5, label='Underweight (<18.5)')
        plt.axhline(y=25.0, color='#e67e22', linestyle='--', alpha=0.5, label='Overweight (>=25)')
        plt.axhline(y=30.0, color='#c0392b', linestyle='--', alpha=0.5, label='Obese (>=30)')
        
        plt.title(f"BMI Progress for {name}")
        plt.xlabel("Date & Time")
        plt.ylabel("BMI Value")
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.legend(loc='best')
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
