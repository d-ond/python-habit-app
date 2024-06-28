import sqlite3
from datetime import datetime, timedelta
from DatabaseConnection import DatabaseConnection

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        with DatabaseConnection(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS dates (date TEXT PRIMARY KEY)")
            conn.execute("CREATE TABLE IF NOT EXISTS habits (habit_id INTEGER PRIMARY KEY AUTOINCREMENT, habit_name TEXT UNIQUE)")
            conn.execute("CREATE TABLE IF NOT EXISTS habit_tracker (date TEXT, habit_id INTEGER, status INTEGER DEFAULT 0, FOREIGN KEY (date) REFERENCES dates(date), FOREIGN KEY (habit_id) REFERENCES habits(habit_id), PRIMARY KEY (date, habit_id))")
            self.add_previous_dates(conn)
    
    def add_previous_dates(self, conn):
        date_end = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        date_start = date_end - timedelta(days=15)
        date_list = []

        while date_start.date() <= date_end.date():
            date_list.append(date_start.strftime("%Y-%m-%d"))
            date_start += timedelta(days=1)

        conn.executemany("INSERT OR IGNORE INTO dates (date) VALUES (?)", [(date,) for date in date_list])
        conn.commit()