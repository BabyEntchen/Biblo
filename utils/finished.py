from utils.database import Database
import datetime


def add_read_book():
    db = Database("books.db").create_database()
    year = datetime.date.today().year
    existing = db.fetchone("SELECT * FROM finished WHERE year = ?", (year,))
    if existing:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        current = get_read(yesterday.isoformat())
        db.execute("UPDATE finished SET current = ? WHERE year = ?", (current + 1, year))
    else:
        db.execute("INSERT INTO finished (year, current) VALUES (?, ?)", (year, 1))



def set_read(value):
    db = Database("books.db").create_database()
    year = datetime.date.today().year
    existing = db.fetchone("SELECT year FROM finished WHERE year = ?", (year,))
    if existing:
        db.execute("UPDATE finished SET current = ? WHERE year = ?", (value, year))
    else:
        db.execute("INSERT INTO finished (year, current) VALUES (?, ?)", (year, value,))


def get_read(year=None):
    db = Database("books.db").create_database()
    if not year:
        year = datetime.date.today().year
    current = db.fetchone("SELECT current FROM finished WHERE year = ?", (year,))
    if current:
        return current[0]
    else:
        return 0


