import string
from utils.database import Database
from flask import Flask, render_template, request, redirect, flash
from utils.books import Book, get_books
from markupsafe import escape
from string_py import Str
from utils.streak import *
from datetime import datetime
from utils.progress import ReadingProgress
from utils.finished import get_read

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    search = request.form.get('search', None)
    return render_index(search)


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def add_form():
    isbn = request.form['isbn']
    points = request.form.get('points', None)
    review = request.form.get('review', None)
    pages = request.form.get('pages', None)
    code = int(Str("1234567890").generate(length=9))
    if isbn:
        book = Book.isbn_get(isbn)
        try:
            book.save()
        except Exception as e:
            return render_template('add.html', error="Something went wrong. Error: " + str(e))
        if points:
            book.add_rating(code, points)
        if review:
            book.add_review(code, review)
        if pages:
            ReadingProgress.create_new(book, int(pages))

        return redirect('/')
    elif search := request.form['search']:
        books = Book.new_search(search)
        return render_template('add.html', search_results=books)


@app.route('/add/custom')
def add_custom():
    return render_template('custom.html')


@app.route('/add/custom', methods=['POST'])
def add_custom_form():
    isbn = request.form['isbn']
    pages = request.form['pages']
    title = request.form['title']
    author = request.form['author']
    publisher = request.form['publisher']
    published = request.form['published']
    cover_url = request.form['image']
    book = Book.create(isbn, title, cover_url, author, None, publisher, published)
    ReadingProgress.create_new(book, pages)
    try:
        book.save()
    except Exception as e:
        return render_template('custom.html', error="Something went wrong. Error: " + str(e))
    return redirect('/')


# In app.py
@app.route('/book/<isbn>', strict_slashes=False, methods=['GET', 'POST'])
def book(isbn):
    book = Book.get_book(escape(isbn))
    progress = book.progress()
    if request.method == 'POST':
        new_progress = request.form.get('progress')
        if new_progress is not None:
            try:
                progress.update_progress(int(new_progress))
            except Exception as e:
                pass
                # flash(f"Fehler beim Aktualisieren des Fortschritts: {e}")
    reviews = book.get_reviews()
    return render_template('book.html', book=book, reviews=reviews, progress=progress, percent=progress.progress_percentage())


@app.route('/book/<isbn>/delete')
def delete(isbn):
    book = Book.get_book(escape(isbn))
    book.delete()
    return redirect('/')


@app.route('/book/<isbn>/rate/')
def review(isbn):
    book = Book.get_book(escape(isbn))
    return render_template('rate.html', book=book)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        goal = request.form.get('goal')
        finished = request.form.get('finished')
        streak = request.form.get('streak')

        year = datetime.now().year
        db = Database("books.db").create_database()

        if goal:
            existing = db.fetchone("SELECT number FROM goal WHERE year = ?", (year,))
            if existing:
                db.execute("UPDATE goal SET number = ? WHERE year = ?", (goal, year))
            else:
                db.execute("INSERT INTO goal (year, number) VALUES (?, ?)", (year, goal))

        if finished:
            db.execute("UPDATE finished SET current = ? WHERE year = ?", (finished, year))

        if streak:
            set_streak(int(streak))

        return redirect('./')
    goal = Database("books.db").fetchone("SELECT number FROM goal WHERE year = ?", (datetime.now().year,))
    goal = goal[0] if goal else None
    return render_template('settings.html', goal=goal if goal else 0, streak=get_streak(),
                           finished=get_read())


@app.route('/book/<isbn>/rate/', methods=['POST'])
def review_form(isbn):
    points = request.form.get('points', None)
    review = request.form.get('review', None)
    code = int(Str("1234567890").generate(length=9))
    book = Book.get_book(escape(isbn))
    if points:
        book.add_rating(code, points)
    if review:
        book.add_review(code, review)
    return redirect('/book/' + isbn)


@app.route('/read_today')
def read_today():
    add_read_day()
    return redirect('/')


def render_index(search=None):
    Database("books.db").create_database()
    books = get_books(search)
    goal = Database("books.db").fetchone("SELECT number FROM goal WHERE year = ?", (datetime.now().year,))
    goal = goal[0] if goal else None
    return render_template('index.html', book_list=[book for book in books], streak=get_streak(),
                           finished=get_read(),
                           goal=goal if goal else 0)


if __name__ == '__main__':
    app.run()
