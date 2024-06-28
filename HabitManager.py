import sqlite3
from datetime import datetime, timedelta

# file for managing (add, delete, updating) the habits in the database

class HabitManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.update_dates()

    def get_habits(self):
        self.cursor.execute("SELECT * FROM habits")
        return self.cursor.fetchall()

    def get_dates(self):
        self.cursor.execute("SELECT * FROM dates ORDER BY date DESC")
        return self.cursor.fetchall()

    def get_habit_statuses(self):
        self.cursor.execute("SELECT h.habit_name, d.date, ht.status "
            + "FROM habit_tracker ht "
            + "JOIN dates d ON ht.date = d.date "
            + "JOIN habits h ON ht.habit_id = h.habit_id "
            + "ORDER BY h.habit_name, d.date"
        )
        return self.cursor.fetchall()
    
    def add_habit(self, habit):
        try:
            self.cursor.execute("INSERT INTO habits (habit_name) VALUES (?)", (habit,))
            self.conn.commit()

            self.cursor.execute("SELECT habit_id FROM habits WHERE habit_name = ?", (habit,))
            habit_id = self.cursor.fetchone()[0]

            add_into_dates = f"INSERT INTO habit_tracker (date, habit_id, status) SELECT date, {habit_id}, 0 FROM dates"
            self.cursor.execute(add_into_dates)
            self.conn.commit()
        except: 
            return
    
    def delete_habit(self, habit):
        try:
            self.cursor.execute("DELETE FROM habit_tracker WHERE habit_id = (SELECT habit_id FROM habits WHERE habit_name = ?)", (habit,))
            self.cursor.execute("DELETE FROM habits WHERE habit_name = ?", (habit,))
            self.conn.commit()
        except:
            return

    def toggle_habit_status(self, habit_name, date):
        try:
            self.cursor.execute(
                "UPDATE habit_tracker SET status = CASE status WHEN 1 THEN 0 ELSE 1 END "
                "WHERE habit_id = (SELECT habit_id FROM habits WHERE habit_name = ?) AND date = ?",
                (habit_name, date)
            )
            self.conn.commit()
        except:
            return

    def update_dates(self):
        self.cursor.execute("SELECT date FROM dates ORDER BY date DESC LIMIT 1")
        last_date = self.cursor.fetchone()
        start_date = datetime.strptime(last_date[0], "%Y-%m-%d") if last_date else datetime.now()

        current_date = datetime.now()
        date_list = []

        while start_date.date() <= current_date.date():
            date_list.append(start_date.strftime("%Y-%m-%d"))
            start_date += timedelta(days=1)

        self.cursor.executemany("INSERT OR IGNORE INTO dates (date) VALUES (?)", [(date,) for date in date_list])
        self.conn.commit()

        self.cursor.execute("SELECT habit_id FROM habits")
        habit_ids = [habit[0] for habit in self.cursor.fetchall()]

        for habit_id in habit_ids:
            self.cursor.executemany(
                "INSERT OR IGNORE INTO habit_tracker (date, habit_id, status) VALUES (?, ?, 0)",
                [(date, habit_id) for date in date_list]
            )
        self.conn.commit()
