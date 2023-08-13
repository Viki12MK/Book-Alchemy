import requests
import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import Author, Book


# Create an instance of SQLAlchemy
db = SQLAlchemy()

# Create an instance of the Flask application
app = Flask(__name__)

# Configure the database connection:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/user/Desktop/POVTORUVANJE/107/107.2/' \
                                        'LIBRARY_ALCHEMY/book-alchemy/data/library.sqlite'
db.init_app(app)


@app.route('/')
@app.route('/<sort_option>')
def home(sort_option='title'):
    if sort_option == 'title':
        books_data = db.session.query(Book, Author).\
            join(Author, Book.author_id == Author.author_id).order_by(Book.title).all()
    elif sort_option == 'author':
        books_data = db.session.query(Book, Author).\
            join(Author, Book.author_id == Author.author_id).order_by(Author.author_name).all()
    else:
        books_data = db.session.query(Book, Author).join(Author, Book.author_id == Author.author_id).all()

    books = []
    for book, author in books_data:
        book.cover_url = get_cover_url(book.isbn)
        book.author_name = author.author_name
        books.append(book)
    return render_template('home.html', books=books)


def get_cover_url(isbn):
    api_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

    response = requests.get(api_url)
    print(f"ISBN: {isbn}, Status Code: {response.status_code}")
    if response.status_code == 200:
        return api_url
    return None


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        books_data = db.session.query(Book, Author). \
            join(Author, Book.author_id == Author.author_id). \
            filter(Book.title.ilike(f"%{search_query}%") | Author.author_name.ilike(f"%{search_query}%")).all()

        books = []
        for book, author in books_data:
            book.cover_url = get_cover_url(book.isbn)
            book.author_name = author.author_name
            books.append(book)

        if len(books) == 0:
            message = "No books match the search criteria."
        else:
            message = None

        return render_template('search_results.html', books=books, message=message)

    return redirect(url_for('home'))


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        birth_date_str = request.form['birth_date']
        birth_date=None
        if birth_date_str:
            birth_date = datetime.datetime.strptime(birth_date_str, '%Y-%m-%d').date()

        date_of_death_str = request.form['date_of_death']
        date_of_death = None
        if date_of_death_str:
            date_of_death = datetime.datetime.strptime(date_of_death_str, '%Y-%m-%d').date()

        author = Author(
            author_name=request.form['author_name'],
            birth_date=birth_date,
            date_of_death=date_of_death,
        )
        db.session.add(author)
        db.session.commit()
    return render_template("/add_author.html")




@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book = Book(
            isbn=request.form['isbn'],
            title=request.form['title'],
            publication_year=request.form['publication_year'],
            author_id=request.form['author_id'],  # Use author_id instead of author_name
        )
        db.session.add(book)
        db.session.commit()

    authors = db.session.query(Author).all()
    return render_template("/add_book.html", authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = db.session.query(Book).filter_by(book_id=book_id).first()

    if book:
        db.session.delete(book)
        db.session.commit()

        return redirect(url_for('home', message='Book deleted successfully.'))

    return redirect(url_for('home', message='Book not found.'))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)