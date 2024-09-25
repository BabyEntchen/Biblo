import sqlite3


class Review:
    def __init__(self, review_id, isbn, text):
        self.review_id = review_id
        self.isbn = isbn
        self.text = text

    @property
    def rating(self):
        conn = sqlite3.connect("books.db")
        c = conn.cursor()
        c.execute("SELECT * FROM ratings WHERE review_id = ?", (self.review_id,))
        rating = c.fetchone()
        conn.close()
        if rating is None:
            return None
        return rating[3]
