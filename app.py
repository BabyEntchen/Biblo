from flask import Flask, render_template
from utils.books import Book

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', book_list=[Book.isbn_get("9783837641097"), Book.isbn_get("9783551551672")])


@app.route('/add')
def add():
    return render_template('add.html')


if __name__ == '__main__':
    app.run()
