from utils.database import Database
import datetime


def add_read_day():
    db = Database("books.db").create_database()
    today = datetime.date.today().isoformat()
    existing = db.fetchone("SELECT date FROM streak WHERE date = ?", (today,))
    if not existing:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        current = get_streak(yesterday.isoformat())
        db.execute("INSERT INTO streak (date, current) VALUES (?, ?)", (today, current + 1,))


def set_streak(value):
    db = Database("books.db").create_database()
    today = datetime.date.today().isoformat()
    existing = db.fetchone("SELECT date FROM streak WHERE date = ?", (today,))
    if existing:
        db.execute("UPDATE streak SET current = ? WHERE date = ?", (value, today))
    else:
        db.execute("INSERT INTO streak (date, current) VALUES (?, ?)", (today, value,))


def get_streak(date=None):
    db = Database("books.db").create_database()
    if not date:
        date = datetime.date.today().isoformat()
    current = db.fetchone("SELECT current FROM streak WHERE date = ?", (date,))
    if current:
        return current[0]
    else:
        return 0


