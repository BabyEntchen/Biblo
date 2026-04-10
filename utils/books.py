import requests
from utils.database import Database
from .reviews import Review
from string_py import Str
from utils.progress import ReadingProgress


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
        response = requests.get(f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json")
        if response.status_code == 200 or response.json == {}:
            data = response.json()
            # title, author = api_isbn_datas(data)
            for record_key, record_value in data["records"].items():
                # Titel und Autoren
                title = record_value["data"].get("title", "Kein Titel")
                author = ", ".join([a["name"] for a in record_value["data"].get("authors", [])])

                # Verlag (falls vorhanden)
                details = record_value.get("details", {}).get("details", {})
                publisher = None
                if "publishers" in details:
                    publisher = ", ".join(details.get("publishers", []))
                elif "publisher" in details:
                    publisher = details.get("publisher")
                else:
                    publisher = "Unbekannt"

                # Veröffentlichungsdatum
                publish_date = details.get("publish_date", "Unbekannt")

                # Thumbnail-URL (nimm das erste aus items, falls vorhanden)
                thumbnail = None
                if "items" in data and len(data["items"]) > 0:
                    thumbnail = data["items"][0].get("cover", {}).get("small", None)
                else:
                    thumbnail = None

            # price = book_data["details"].get("price")
            # publisher = ", ".join(book_data["details"].get("publishers"))
            # published = book_data["details"].get("publish_date")
            # cover_url = book_data.get("thumbnail_url")
            return cls(isbn, title, thumbnail, author, None, publisher, publish_date)
        else:
            raise Exception("ISBN was not found.")
        return None


    @classmethod
    def key_get(cls, key):
        response = requests.get(f"https://openlibrary.org{key}.json")
        if response.status_code == 200:
            data = response.json()
            # isbn = data.get()


            isbn = data.get("isbn_10", [None])[0] or data.get("isbn_13", [None])[0]
            if not isbn:
                response = requests.get(f"https://openlibrary.org{key}/editions.json")
                data = response.json().get("entries")[0]
                isbn = data.get("isbn_13", [None])[0] or response.json().get("editions", [{}])[0].get("isbn_10", [None])[0]
                if not isbn:
                    return None
                    # raise Exception("ISBN not found in the book data.")

            return cls.isbn_get(isbn)

            # datas = requests.get(f"https://openlibrary.org/api/volumes/brief/isbn/{isbn}.json")
            #
            # for record_key, record_value in datas.json()["records"].items():
            #     title = record_value["data"].get("title", "Kein Titel")
            #     authors = [author["name"] for author in record_value["data"].get("authors", [])]
            #
            # price = None
            # return cls(isbn, title, data.get("thumbnail_url"), ", ".join(authors), price, data.get("publishers", ["Unknown"])[0], data.get("publish_date", "Unknown"))

    @classmethod
    def get_book(cls, isbn):
        db = Database("books.db")
        book = db.fetchone("SELECT * FROM books WHERE isbn = ?", (int(isbn),))
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
    def new_search(query):
        response = requests.get(f"https://openlibrary.org/search.json?q={query.replace(' ', '+')}")
        if response.status_code == 200:
            result = []
            data = response.json()
            for num, doc in enumerate(data["docs"]):
                key = doc['key']
                book = Book.key_get(key)
                if book:
                    result.append(book)
            return result
        else:
            raise Exception("Search failed.")

    @staticmethod
    def search(query):
        response = requests.get(f"https://openlibrary.org/search.json?q={query.replace(' ', '+')}")
        if response.status_code == 200:
            data = response.json()
            try:
                key = data["docs"][0]['isbn']
            except IndexError:
                key = []
            result = []
            for book in key:
                try:
                    book = Book.isbn_get(key)
                except Exception:
                    book = None
                if book:
                    result.append(book)
            return result
        else:
            raise Exception("Search failed.")

    def add_rating(self, id_, points):
        self.db.execute("INSERT INTO ratings VALUES (?, ?, ?, ?)", (id_, int(self.isbn), "points", points))

    def get_rating(self):
        ratings = self.db.fetchall("SELECT * FROM ratings WHERE isbn = ?", (int(self.isbn),))
        if len(ratings) == 0:
            return None
        avrg = 0
        for rating in ratings:
            avrg += rating[3]
        avrg /= len(ratings)
        return avrg

    def add_review(self, id_, review):
        self.db.execute("INSERT INTO reviews VALUES (?, ?, ?)", (id_, int(self.isbn), review))

    def get_review(self, review):
        return self.db.fetchone("SELECT * FROM reviews WHERE isbn = ? AND review = ?", (int(self.isbn), review))

    def delete_review(self, review):
        self.db.execute("DELETE FROM reviews WHERE isbn = ? AND review = ?", (int(self.isbn), review))

    def get_raw_reviews(self):
        return self.db.fetchall("SELECT * FROM reviews WHERE isbn = ?", (int(self.isbn),))

    def get_reviews(self):
        return [Review(*review) for review in self.get_raw_reviews()]

    def delete(self):
        self.db.execute("DELETE FROM books WHERE isbn = ?", (int(self.isbn),))

    def progress(self):
        return ReadingProgress.from_db(self)

    def get_percent(self):
        progress = self.progress
        if progress:
            return progress.progress_percentage()
        return 0

    @property
    def percent(self):
        return self.get_percent()

    @property
    def rating(self):
        return self.get_rating()



    def __str__(self):
        return f"{self.title} by {self.author} - {self.price}"


def get_books(name=None):
    if name:
        return [Book(*book) for book in Database("books.db").fetchall("SELECT * FROM books WHERE title LIKE ?", (f"%{name}%",))]
    return [Book(*book) for book in Database("books.db").fetchall("SELECT * FROM books")]


# class DetailedBook(Book):
#     def __init__(self, isbn, title, cover_url, author, price, publisher, published):
#         super().__init__(isbn, title, cover_url, author, price, publisher, published)
#         self.reviews = self.get_reviews()
#         self.rating = self.get_rating()
#
#     def __dict__(self):
#         data = super().__dict__()
#         data["reviews"] = [review.__dict__() for review in self.reviews]
#         data["rating"] = self.rating
#         return data
