from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship


Base = declarative_base()

# Create a database connection
engine = create_engine('sqlite:///data/library.sqlite')

# Create a database session
Session = sessionmaker(bind=engine)
session = Session()


class Author(Base):
    __tablename__ = 'authors'

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    author_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    date_of_death = Column(Date, nullable=True)

    def __repr__(self):
        return f"Author(author_id = {self.author_id}, author_name = {self.author_name}, " \
               f"birth_date = {self.birth_date}, date_of_death = {self.date_of_death}"

    def __str__(self):
        return f"Author: {self.author_name}"

    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String, nullable=False)
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.author_id'))

    def __repr__(self):
        return f"<Book(book_id={self.book_id}, isbn='{self.isbn}', title='{self.title}', " \
               f"publication_year={self.publication_year}, author_id={self.author_id})>"

    def __str__(self):
        return f"Book: {self.title} ({self.publication_year})"

    author = relationship("Author", back_populates="books")


Base.metadata.create_all(engine)
