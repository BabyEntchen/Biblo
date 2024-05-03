from flask import Flask, render_template, request
from utils.books import Book, get_books

app = Flask(__name__)


@app.route('/')
def index():
    return render_index()


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def add_form():
    isbn = request.form['isbn']
    book = Book.isbn_get(isbn)
    try:
        book.save()
    except Exception as e:
        return render_template('add.html', error="Something went wrong. Error: " + str(e))
    return render_index()


def render_index():
    books = get_books()
    return render_template('index.html', book_list=[book for book in books])


if __name__ == '__main__':
    app.run()
