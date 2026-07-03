# backend/database.py
import sqlite3
from datetime import datetime

DB_PATH = "backend/routeiq.db"

def init_db():
    """Initializes the SQLite database and creates the batch history table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            scenario TEXT NOT NULL,
            num_stops INTEGER NOT NULL,
            baseline_eta REAL NOT NULL,
            optimized_eta REAL NOT NULL,
            efficiency_gain REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_batch(scenario, num_stops, baseline_eta, optimized_eta, efficiency_gain):
    """Saves an optimization summary run to the persistent ledger."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO batch_history (timestamp, scenario, num_stops, baseline_eta, optimized_eta, efficiency_gain)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), scenario, num_stops, baseline_eta, optimized_eta, efficiency_gain))
    conn.commit()
    conn.close()

def get_batch_history():
    """Fetches all past calculation logs to display in the frontend dataframe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, scenario, num_stops, baseline_eta, optimized_eta, efficiency_gain FROM batch_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows