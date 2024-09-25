import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_database(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS books (isbn INTEGER PRIMARY KEY, title TEXT, thumbnail_url TEXT, author TEXT, price TEXT, publisher TEXT, published TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS reviews (review_id INTEGER PRIMARY KEY, isbn INTEGER, review TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS ratings (review_id INTEGER PRIMARY KEY, isbn INTEGER, category TEXT, rating INTEGER)")
        conn.commit()
        conn.close()
        return self

    def execute(self, query, values):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(query, values)
        conn.commit()
        conn.close()

    def fetchall(self, query, values=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if values is None:
            c.execute(query)
        else:
            c.execute(query, values)
        result = c.fetchall()
        conn.close()
        return result

    def fetchone(self, query, values):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(query, values)
        result = c.fetchone()
        conn.close()
        return result
