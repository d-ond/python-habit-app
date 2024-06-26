import tkinter as tk
from tkinter import ttk
import sqlite3

class HabitManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_habits(self):
        self.cursor.execute("SELECT * FROM habits")
        return self.cursor.fetchall()

    def get_dates(self):
        self.cursor.execute("SELECT * FROM dates ORDER BY date ASC")
        return self.cursor.fetchall()

    def get_habit_statuses(self):
        self.cursor.execute(
            "SELECT h.habit_name, d.date, ht.status " +
            "FROM habit_tracker ht " +
            "JOIN dates d ON ht.date = d.date " +
            "JOIN habits h ON ht.habit_id = h.habit_id " +
            "ORDER BY h.habit_name, d.date"
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
        except sqlite3.Error as e:
            print(f"Error - {e}")
        return
    
    def delete_habit(self, habit):
        try:
            self.cursor.execute("DELETE FROM habit_tracker WHERE habit_id = (SELECT habit_id FROM habits WHERE habit_name = ?)", (habit,))
            self.cursor.execute("DELETE FROM habits WHERE habit_name = ?", (habit,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error - {e}")

class HabitApp:
    def __init__(self, root, habit_manager):
        self.root = root
        self.habit_manager = habit_manager
        self.root.title("Habit Tracker")

        dates = self.habit_manager.get_dates()
        columns = ["Habit"] + [date[0] for date in dates]

        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings',
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        for i in range(len(columns)):
            self.tree.heading(columns[i], text=columns[i])
            if i == 0:
                self.tree.column(columns[i], width=75, minwidth=75, stretch=tk.YES)
            else:
                self.tree.column(columns[i], width=25, minwidth=25, stretch=tk.YES)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.display_habits()

    def display_habits(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        habit_statuses = self.habit_manager.get_habit_statuses()

        habits = {}
        for habit_name, date, status in habit_statuses:
            if habit_name not in habits:
                habits[habit_name] = {}
            habits[habit_name][date] = "✓" if status == 1 else "X"

        dates = [date[0] for date in self.habit_manager.get_dates()]

        for habit_name, statuses in habits.items():
            values = [habit_name] + [statuses.get(date, "") for date in dates]
            self.tree.insert("", "end", values=values)

def add_habit():
    def submit_habit():
        habit = habit_var.get()
        habit_manager.add_habit(habit)
        add_win.destroy()
        app.display_habits()

    add_win = tk.Toplevel(root)
    habit_var = tk.StringVar()

    entry = tk.Entry(add_win, textvariable=habit_var)
    entry.grid(row=0, column=0)

    sub_btn = tk.Button(add_win, text='Submit', command=submit_habit)
    sub_btn.grid(row=1, column=0)

def delete_habit():
    def submit_delete():
        habit = habit_var.get()
        habit_manager.delete_habit(habit)
        delete_win.destroy()
        app.display_habits()

    delete_win = tk.Toplevel(root)
    habit_var = tk.StringVar()

    entry = tk.Entry(delete_win, textvariable=habit_var)
    entry.grid(row=0, column=0)

    sub_btn = tk.Button(delete_win, text='Submit', command=submit_delete)
    sub_btn.grid(row=1, column=0)

root = tk.Tk()
root.title("Habit Tracker")
root.geometry("450x800")
root.config(bg="black")

habit_manager = HabitManager('test.db')
app = HabitApp(root, habit_manager)

menu_bar = tk.Menu(root)
habit_menu = tk.Menu(menu_bar, tearoff=0)
habit_menu.add_command(label="Create Habit", command=add_habit)
habit_menu.add_command(label="Delete Habit", command=delete_habit)
habit_menu.add_separator()
habit_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="Habits", menu=habit_menu)
root.config(menu=menu_bar)

root.mainloop()
