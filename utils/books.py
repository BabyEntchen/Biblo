import requests
from utils.database import Database


class Book:
    def __init__(self, isbn, title, cover_url, author, price, publisher, published):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.price = price
        self.publisher = publisher
        self.published = published
        self.cover_url = cover_url
        self.db = Database("books.db").create_database()

    @classmethod
    def create(cls, isbn, title, cover_url, author, price, publisher, published):
        return cls(isbn, title, cover_url, author, price, publisher, published)

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["isbn"],
            data["title"],
            data["author"],
            data["price"],
            data["publisher"],
            data["published"],
            data["cover_url"]
        )


    @classmethod
    def isbn_get(cls, isbn):
        isbn = isbn.replace("-", "")
        response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json")
        if response.status_code == 200 or response.json == {}:
            data = response.json()
            book_data = data["ISBN:" + isbn]
            title = book_data["details"].get("title")
            try:
                author = book_data["details"].get("authors")[0]["name"]
            except TypeError:
                author = "Unknown"
            price = book_data["details"].get("price")
            publisher = ", ".join(book_data["details"].get("publishers"))
            published = book_data["details"].get("publish_date")
            cover_url = book_data.get("thumbnail_url")
            return cls(isbn, title, cover_url, author, price, publisher, published)
        else:
            raise Exception("ISBN was not found.")
        return None

    @classmethod
    def get_book(cls, isbn):
        db = Database("books.db")
        book = db.fetchone("SELECT * FROM books WHERE isbn = ?", (int(isbn),))
        print(book)
        return cls(*book)

    def save(self):
        self.db.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)", (int(self.isbn), self.title, self.cover_url, self.author, self.price, self.publisher, self.published))


    def __dict__(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "price": self.price,
            "publisher": self.publisher,
            "published": self.published,
            "cover_url": self.cover_url
        }

    @staticmethod
    def search(query):
        response = requests.get(f"https://openlibrary.org/search.json?q={query.replace(' ', '+')}")
        if response.status_code == 200:
            data = response.json()
            try:
                books = data["docs"][0]['isbn']
            except IndexError:
                books = []
            result = []
            for book in books:
                try:
                    book = Book.isbn_get(book)
                except Exception:
                    book = None
                if book:
                    result.append(book)
            return result
        else:
            raise Exception("Search failed.")

    def add_rating(self, points):
        self.db.execute("INSERT INTO ratings VALUES (?, ?, ?)", (int(self.isbn), "points", points))

    def get_rating(self):
        ratings = self.db.fetchall("SELECT * FROM ratings WHERE isbn = ?", (int(self.isbn),))
        if len(ratings) == 0:
            return None
        avrg = 0
        for rating in ratings:
            avrg += rating[2]
        avrg /= len(ratings)
        return avrg

    def get_reviews(self):
        return self.db.fetchall("SELECT * FROM reviews WHERE isbn = ?", (int(self.isbn),))

    @property
    def rating(self):
        return self.get_rating()


    def __str__(self):
        return f"{self.title} by {self.author} - {self.price}"


def get_books(name=None):
    if name:
        return [Book(*book) for book in Database("books.db").fetchall("SELECT * FROM books WHERE title LIKE ?", (f"%{name}%",))]
    return [Book(*book) for book in Database("books.db").fetchall("SELECT * FROM books")]
