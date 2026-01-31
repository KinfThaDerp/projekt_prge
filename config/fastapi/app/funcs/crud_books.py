def fetch_books() -> list:
    query = """
            SELECT * FROM book;
            """
    cursor.execute(query)
    books = cursor.fetchall()
    return books

def fetch_book(book_id: int) -> tuple[int, str, str, str | None, str | None, str | None]:
    query = """
            SELECT id, title, author, isbn_13, publisher, genre 
            FROM book WHERE id = %s; \
            """
    cursor.execute(query, (book_id,))
    return cursor.fetchone()

def insert_book(cursor, title: str, author: str, isbn_13: str | None, publisher: str | None, genre: str | None) -> int:
    query = """
        INSERT INTO book (title, author, isbn_13, publisher, genre)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    cursor.execute(query, (title, author, isbn_13, publisher, genre))
    return cursor.fetchone()[0]



def update_book(cursor, book_id: int, **kwargs) -> None:
    query = """
                UPDATE book SET {} WHERE id = %s;
                """.format(
        ", ".join(f"{key} = %s" for key in kwargs.keys())
    )
    cursor.execute(query, (*kwargs.values(), book_id))

