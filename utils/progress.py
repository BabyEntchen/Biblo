from utils.database import Database


class ReadingProgress:
    def __init__(self, book, pages: int, progress: int = 0):
        self.book = book
        self.pages = pages
        self.progress = progress
        self.db = Database("books.db").create_database()

    @classmethod
    def from_db(cls, book):
        db = Database("books.db").create_database()
        result = db.fetchone("SELECT progress, pages FROM progress WHERE isbn = ?", (book.isbn,))
        if result:
            progress, pages = result
            return cls(book, int(pages), int(progress))
        else:
            return cls(book, pages=0, progress=0)

    @classmethod
    def create_new(cls, book, pages):
        instance = cls(book, pages, progress=0)
        instance.save()
        return instance

    def update_progress(self, new_progress):
        if 0 <= new_progress <= self.pages:
            self.progress = new_progress
            self.db.execute(
                "UPDATE progress SET progress = ? WHERE isbn = ?", new_progress, self.book.isbn)
        else:
            raise ValueError("Progress must be between 0 and the total number of pages.")

    def edit_pages(self, new_pages):
        if new_pages >= self.progress:
            self.pages = new_pages
            self.db.execute(
                "UPDATE progress SET pages = ? WHERE isbn = ?", new_pages, self.book.isbn)
        else:
            raise ValueError("Total pages cannot be less than current progress.")

    def progress_percentage(self):
        return round((self.progress / self.pages) * 100 if self.pages > 0 else 0)

    def save(self):
        self.db.execute("INSERT OR REPLACE INTO progress (isbn, progress, pages) VALUES (?, ?, ?)",
                        (self.book.isbn, self.progress, self.pages))

    def __str__(self):
        return f"ReadingProgress(book={self.book.title}, progress={self.progress}/{self.pages} pages, {self.progress_percentage():.2f}%)"
