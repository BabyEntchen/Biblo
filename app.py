import string
from utils.database import Database
from flask import Flask, render_template, request, redirect
from utils.books import Book, get_books
from markupsafe import escape
from string_py import Str

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

        return redirect('/')
    elif search := request.form['search']:
        books = Book.search(search)
        return render_template('add.html', search_results=books)


@app.route('/add/custom')
def add_custom():
    return render_template('custom.html')


@app.route('/add/custom', methods=['POST'])
def add_custom_form():
    isbn = request.form['isbn']
    title = request.form['title']
    author = request.form['author']
    publisher = request.form['publisher']
    published = request.form['published']
    cover_url = request.form['image']
    book = Book.create(isbn, title, cover_url, author, None, publisher, published)
    try:
        book.save()
    except Exception as e:
        return render_template('custom.html', error="Something went wrong. Error: " + str(e))
    return render_index()


@app.route('/book/<isbn>', strict_slashes=False)
def book(isbn):
    book = Book.get_book(escape(isbn))
    reviews = book.get_reviews()
    return render_template('book.html', book=book, reviews=reviews)


@app.route('/book/<isbn>/delete')
def delete(isbn):
    book = Book.get_book(escape(isbn))
    book.delete()
    return redirect('/')


@app.route('/book/<isbn>/rate/')
def review(isbn):
    book = Book.get_book(escape(isbn))
    return render_template('rate.html', book=book)


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


def render_index(search=None):
    Database("books.db").create_database()
    books = get_books(search)
    return render_template('index.html', book_list=[book for book in books])


if __name__ == '__main__':
    app.run()
