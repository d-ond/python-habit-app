import sqlite3
from datetime import datetime, timedelta
from DatabaseConnection import DatabaseConnection

class HabitManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.update_dates()

    def get_habits(self):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits")
            return cursor.fetchall()

    def get_dates(self, limit=0):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            if limit > 0:
                cursor.execute("SELECT * FROM dates ORDER BY date DESC LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT * FROM dates ORDER BY date DESC")
            return cursor.fetchall()

    def get_habit_statuses(self):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT h.habit_name, d.date, ht.status FROM habit_tracker ht JOIN dates d ON ht.date = d.date JOIN habits h ON ht.habit_id = h.habit_id ORDER BY h.habit_name, d.date")
            return cursor.fetchall()

    def add_habit(self, habit):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO habits (habit_name) VALUES (?)", (habit,))
                conn.commit()

                cursor.execute("SELECT habit_id FROM habits WHERE habit_name = ?", (habit,))
                habit_id = cursor.fetchone()[0]

                cursor.execute(f"INSERT INTO habit_tracker (date, habit_id, status) SELECT date, {habit_id}, 0 FROM dates")
                conn.commit()
            except sqlite3.IntegrityError:
                pass

    def delete_habit(self, habit):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM habit_tracker WHERE habit_id = (SELECT habit_id FROM habits WHERE habit_name = ?)", (habit,))
            cursor.execute("DELETE FROM habits WHERE habit_name = ?", (habit,))
            conn.commit()

    def toggle_habit_status(self, habit_name, date):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE habit_tracker SET status = CASE status WHEN 1 THEN 0 ELSE 1 END WHERE habit_id = (SELECT habit_id FROM habits WHERE habit_name = ?) AND date = ?", (habit_name, date))
            conn.commit()

    def update_dates(self):
        with DatabaseConnection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date FROM dates ORDER BY date DESC LIMIT 1")
            last_date = cursor.fetchone()
            start_date = datetime.strptime(last_date[0], "%Y-%m-%d") if last_date else datetime.now()

            current_date = datetime.now()
            date_list = []

            while start_date.date() <= current_date.date():
                date_list.append(start_date.strftime("%Y-%m-%d"))
                start_date += timedelta(days=1)

            cursor.executemany("INSERT OR IGNORE INTO dates (date) VALUES (?)", [(date,) for date in date_list])
            conn.commit()

            cursor.execute("SELECT habit_id FROM habits")
            habit_ids = [habit[0] for habit in cursor.fetchall()]

            for habit_id in habit_ids:
                cursor.executemany("INSERT OR IGNORE INTO habit_tracker (date, habit_id, status) VALUES (?, ?, 0)", [(date, habit_id) for date in date_list])
            conn.commit()
