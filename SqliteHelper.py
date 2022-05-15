import sqlite3


class SqliteHelper:

    def __init__(self, name=None):
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
            print(sqlite3.version)
        except sqlite3.Error as e:
            print("Failed connecting to database...")

    def create_table(self):
        c = self.cursor
        c.execute("""CREATE TABLE IF NOT EXISTS xe_gui(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    so_xe TEXT NOT NULL,
                    ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")

    def edit(self, query):  # INSERT & UPDATE
        c = self.cursor
        c.execute(query)
        self.conn.commit()

    def select(self, query):  # SELECT
        c = self.cursor
        c.execute(query)
        return c.fetchall()

    def getLastRowId(self):
        c = self.cursor
        return c.lastrowid


test = SqliteHelper("gui_xe.db")
test.create_table()

#test.edit("INSERT INTO xe_gui (so_xe) VALUES ('XXXXX-XXXX')")
#test.edit("UPDATE users SET name='jack' WHERE name = 'john'")
#print(test.select("SELECT * FROM xe_gui"))
