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
        if response.status_code == 200:
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
        book = db.execute("SELECT * FROM books WHERE isbn = ?", (isbn,))
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


    def __str__(self):
        return f"{self.title} by {self.author} - {self.price}"


def get_books():
    return [Book(*book) for book in Database("books.db").fetch("SELECT * FROM books")]
