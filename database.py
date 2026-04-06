import sqlite3

def init_db():
    # This creates a file named 'skincare_app.db' in your current folder
    conn = sqlite3.connect('skincare_app.db')
    cursor = conn.cursor()

    # Table 1: The custom schedule template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            day_number INTEGER NOT NULL
        )
    ''')

    # Table 2: The internal clock for the cycle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Cycle_State (
            id INTEGER PRIMARY KEY CHECK (id = 1), -- Forces only one row to ever exist
            current_day_number INTEGER DEFAULT 1,
            last_checked_date DATE
        )
    ''')

    # Table 3: The audit trail of commands
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Command_History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_description TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Initialize the Cycle_State with its single required row if it is empty
    cursor.execute('INSERT OR IGNORE INTO Cycle_State (id, current_day_number) VALUES (1, 1)')

    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

if __name__ == '__main__':
    init_db()
