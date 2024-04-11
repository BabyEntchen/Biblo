import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name


    def create_database(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS books (isbn INTEGER PRIMARY KEY, title TEXT, thumbnail_url TEXT, author TEXT, price TEXT, publisher TEXT, published TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS reviews (isbn INTEGER PRIMARY KEY, review TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS ratings (isbn INTEGER PRIMARY KEY, category TEXT, rating INTEGER)")
        conn.commit()
        conn.close()
