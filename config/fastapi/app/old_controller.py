import os
import re
import bcrypt
import psycopg2
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv(verbose=True)


# Database

connection = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)
cursor = connection.cursor()


#  Validation

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.fullmatch(email))


def is_valid_phone_number(phone_number:int) -> bool:
    if (len(str(phone_number)) == 9 or len(str(phone_number)) == 11)  and isinstance(phone_number, int):
        return True
    else:
        return False


#  Password Hashing

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), stored_hash.encode())


#  Web Scraping

header = {
            "User-Agent": "<Mozilla 5/0 (Windows NT 10.0; Win64; x64; Trident/7.0)>",
        }
def scrape_coords(location) -> (float, float):
    url: str = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url, headers=header)
    response_html = BeautifulSoup(response.content, 'html.parser')
    latitude = float((response_html.select('.latitude'))[1].text.replace(',', '.'))
    longitude = float((response_html.select('.longitude'))[1].text.replace(',', '.'))
    return latitude, longitude


def scrape_voivodeship(location) -> str | None:
    url: str = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url, headers=header)
    response_html = BeautifulSoup(response.content, 'html.parser')

    links = response_html.find_all('a', title=True)
    for link in links:
        title = link['title']
        if title.startswith('Województwo '):
            return link.text.strip()
    return None


#  Database

def does_account_with_username_exist(username: str) -> bool:
    query = """
            SELECT 1
            FROM account
            WHERE username = %s
            LIMIT 1;
            """
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None


def does_account_with_email_exist(email: str) -> bool:
    query = """
            SELECT 1
            FROM account
            WHERE email = %s
            LIMIT 1; \
            """
    cursor.execute(query, (email,))
    return cursor.fetchone() is not None


# Database - Inserters

def insert_account(cursor, username: str, email: str, password: str) -> int:
    password_hash = hash_password(password)
    query = """
            INSERT INTO account (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id;
            """
    cursor.execute(query, (username, email, password_hash))
    return cursor.fetchone()[0]


def insert_contact(cursor, phone_number: int | None, email: str | None ) -> int:
    query = """
            INSERT INTO contact (phone_number, email)
            VALUES (%s, %s)
            RETURNING id;
            """
    cursor.execute(query, (phone_number, email))
    return cursor.fetchone()[0]


def insert_address(
    cursor,
    city_id: int | None,
    street: str | None,
    building: str | None,
    apartment: str | None,
    coords: list[float] | tuple[float, float] | None
) -> int:
    if coords and len(coords) == 2:
        lat, lon = coords
    else:
        lat, lon = None, None
    query = """
        INSERT INTO address (city_id, street, building, apartment, coords)
        VALUES (%s, %s, %s, %s, ARRAY[%s, %s]::real[])
        RETURNING id;
    """
    cursor.execute(query, (city_id, street, building, apartment, lat, lon))
    return cursor.fetchone()[0]


def insert_person(
    cursor,
    account_id: int,
    name: str,
    surname: str,
    contact_id: int | None,
    address_id: int | None,
    role: str = 'client'
) -> int:
    query = """
        INSERT INTO person (account_id, name, surname, contact_id, address_id, role)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    cursor.execute(query, (account_id, name, surname, contact_id, address_id, role))
    return cursor.fetchone()[0]


def insert_city(cursor, name: str) -> int | None:
    if not name:
        return None
    voivodeship = scrape_voivodeship(name) or "Unknown"
    try:
        coords = scrape_coords(name)  # (lat, lon)
    except Exception as e:
        print(f"Failed to get coordinates for '{name}': {e}")
        return None
    query = """
        INSERT INTO city (name, voivodeship, coords) 
        VALUES (%s, %s, ARRAY[%s, %s]::real[])
        RETURNING id;
    """
    cursor.execute(query, (name, voivodeship, coords[0], coords[1]))
    return cursor.fetchone()[0]


def insert_book(cursor, title: str, author: str, isbn_13: str | None, publisher: str | None, genre: str | None) -> int:
    query = """
        INSERT INTO book (title, author, isbn_13, publisher, genre)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    cursor.execute(query, (title, author, isbn_13, publisher, genre))
    return cursor.fetchone()[0]





# Database - Updates

def update_person(cursor, person_id: int, **kwargs) -> None:
    query = """
            UPDATE person SET {} WHERE id = %s;
            """.format(
            ", ".join(f"{key} = %s" for key in kwargs.keys())
                )
    cursor.execute(query, (*kwargs.values(), person_id))


def update_book(cursor, book_id: int, **kwargs) -> None:
    query = """
                UPDATE book SET {} WHERE id = %s;
                """.format(
        ", ".join(f"{key} = %s" for key in kwargs.keys())
    )
    cursor.execute(query, (*kwargs.values(), book_id))


def update_library(cursor, library_id: int, **kwargs) -> None:
    query = """
                UPDATE library SET {} WHERE id = %s;
                """.format(
        ", ".join(f"{key} = %s" for key in kwargs.keys())
    )
    cursor.execute(query, (*kwargs.values(), library_id))



# Database - Fetchers

def fetch_people(role: str | None = None) -> list:
    query = """
            SELECT id, account_id, name, surname, contact_id, address_id, role 
            FROM person"""
    if role:
        query += " WHERE role = %s"
        cursor.execute(query, (role,))
    else:
        cursor.execute(query)
    return cursor.fetchall()

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


def fetch_libraries() -> list:
    query = """
        SELECT id, name, address_id, contact_id, city_id
        FROM library;
    """
    cursor.execute(query)
    return cursor.fetchall()


def fetch_library(library_id: int) -> tuple[int, str, int | None, int | None, int]:
    query = """
        SELECT id, name, address_id, contact_id, city_id
        FROM library WHERE id = %s;
    """
    cursor.execute(query, (library_id,))
    return cursor.fetchone()


def fetch_city_id(name: str) -> int | None:
    if not name:
        return None
    query = """
            SELECT id
            FROM city
            WHERE name = %s
            LIMIT 1; \
            """
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    return result[0] if result else None


def fetch_city(person_id: int) -> str | None:
    query = """
            SELECT city.name
            FROM person JOIN address ON person.address_id = address.id JOIN city ON address.city_id = city.id
            WHERE person.id = %s; \
            """
    cursor.execute(query, (person_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def fetch_city_name(city_id: int) -> str | None:
    query = "SELECT name FROM city WHERE id = %s;"
    cursor.execute(query, (city_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def fetch_all_city_names() -> list[str]:
    query = "SELECT DISTINCT name FROM city ORDER BY name;"
    cursor.execute(query)
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def fetch_address(address_id: int) -> tuple[str, str, str, str, list[float]]:
    query = """
        SELECT city.name, address.street, address.building, address.apartment, address.coords
        FROM address
        JOIN city ON address.city_id = city.id
        WHERE address.id = %s;
    """
    cursor.execute(query, (address_id,))
    result = cursor.fetchone()
    return result if result else (None, None, None, None, None)


def fetch_contact(contact_id: int) -> tuple | None:
    query ="""
           SELECT phone_number, email 
           FROM contact 
           WHERE id = %s
            """
    cursor.execute(query, (contact_id,))
    return cursor.fetchone()


def fetch_library_client_ids(library_id: int) -> list[int]:
    query = "SELECT person_id FROM library_client WHERE library_id = %s;"
    cursor.execute(query, (library_id,))
    return [row[0] for row in cursor.fetchall()]


def fetch_library_employee_ids(library_id: int) -> list[int]:
    query = "SELECT person_id FROM library_employee WHERE library_id = %s;"
    cursor.execute(query, (library_id,))
    return [row[0] for row in cursor.fetchall()]


def fetch_employee_library_info(person_id: int) -> tuple[int, str] | None:
    query = """
        SELECT l.id, l.name 
        FROM library l
        JOIN library_employee le ON l.id = le.library_id
        WHERE le.person_id = %s
        LIMIT 1;
    """
    cursor.execute(query, (person_id,))
    return cursor.fetchone()


def fetch_employees_by_city_name(city_name: str) -> list[dict]:
    query = """
        SELECT p.id, p.name, p.surname
        FROM person p
        JOIN address a ON p.address_id = a.id
        JOIN city c ON a.city_id = c.id
        WHERE c.name ILIKE %s AND p.role = 'employee';
    """
    cursor.execute(query, (city_name,))
    rows = cursor.fetchall()
    return [{"id": r[0], "name": f"{r[1]} {r[2]}"} for r in rows]


def fetch_people_details_by_ids(person_ids: list[int]) -> list[dict]:
    if not person_ids:
        return []
    placeholders = ', '.join(['%s'] * len(person_ids))
    query = f"SELECT id, name, surname FROM person WHERE id IN ({placeholders})"

    cursor.execute(query, tuple(person_ids))
    rows = cursor.fetchall()
    return [{"id": row[0], "name": f"{row[1]} {row[2]}"} for row in rows]

def insert_assignment_employee_library(cursor, person_id: int, library_id: int) -> None:
    delete_query = """
                   DELETE FROM library_client 
                   WHERE person_id = %s AND library_id = %s;
                   """
    cursor.execute(delete_query, (person_id, library_id))

    query = """
            INSERT INTO library_employee (person_id, library_id)
            VALUES (%s, %s)
            ON CONFLICT (person_id, library_id) DO NOTHING;
            """
    cursor.execute(query, (person_id, library_id))

    update_role_query = """
                        UPDATE person
                        SET role = 'employee'
                        WHERE id = %s;
                        """
    cursor.execute(update_role_query, (person_id,))


def insert_assignment_client_library(cursor, person_id: int, library_id: int) -> None:
    delete_query = """
                   DELETE FROM library_employee 
                   WHERE person_id = %s AND library_id = %s;
                   """
    cursor.execute(delete_query, (person_id, library_id))

    query = """
            INSERT INTO library_client (person_id, library_id)
            VALUES (%s, %s)
            ON CONFLICT (library_id, person_id) DO NOTHING;
            """
    cursor.execute(query, (person_id, library_id))

    update_role_query = """
                        UPDATE person
                        SET role = 'client'
                        WHERE id = %s;
                        """
    cursor.execute(update_role_query, (person_id,))

def register_account_person(
    username: str,
    email: str,
    password: str,
    confirm_password: str,
    name: str,
    surname: str,
    phone_number: int | None,
    city: str | None,
    street: str | None,
    building: str | None,
    apartment: str | None
,   model=None) -> tuple[bool, str]:
    if password != confirm_password:
        return False, "Passwords do not match"
    if not is_valid_email(email):
        return False, "Invalid email format"
    try:
        with connection:
            with connection.cursor() as cursor:

                if does_account_with_username_exist(username):
                    return False, "Username already exists"
                if does_account_with_email_exist(email):
                    return False, "Email already exists"
                city_id = fetch_city_id(city)
                if city_id is None:
                    city_id = insert_city(cursor, city)
                try:
                    latitude, longitude = scrape_coords(city)
                except Exception:
                    return False, "Invalid city"
                coords = [latitude, longitude]
                account_id = insert_account(cursor, username, email, password)
                contact_id = insert_contact(cursor, phone_number, email)
                address_id = insert_address(cursor,city_id,street,building,apartment, coords)
                insert_person(cursor,account_id,name,surname,contact_id,address_id)
        return True, "User registered successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"error: {e.pgerror}"


def login_account(
        username: str,
        password: str
) -> tuple[bool, str, int | None]:
    if not username or not password:
        return False, "Required fields are missing.", None
    if not does_account_with_username_exist(username):
        return False, "User doesn't exist.", None
    query = """
            SELECT id, password_hash
            FROM account
            WHERE username = %s
            LIMIT 1;
            """
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    account_id, stored_password_hash = result[0], result[1]
    if not verify_password(password, stored_password_hash):
        return False, "Incorrect password.", None
    return True, "Login successful.", account_id


# CRUD - Person

def add_person(
    name: str,
    surname: str,
    account_id: int | None,
    phone_number: str | int | None = None,
    email: str | None = None,
    city: str | None = None,
    street: str | None = None,
    building: str | None = None,
    apartment: str | None = None,
    role: str = 'client',
) -> tuple[bool, str]:
    if not name or not surname:
        return False, "Name and surname are required"
    if role not in ("employee", "client"):
        return False, "Invalid role"
    try:
        with connection:
            with connection.cursor() as cursor:
                city_id = fetch_city_id(city)
                if city and city_id is None:
                    city_id = insert_city(cursor, city)
                coords = None
                if city:
                    try:
                        coords = list(scrape_coords(city))
                    except Exception:
                        return False, "Invalid city"
                contact_id = insert_contact(cursor, phone_number, email)
                address_id = insert_address(cursor,city_id,street,building,apartment,coords)
                insert_person(cursor,account_id,name,surname,contact_id,address_id,role)
        return True, "Person added successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"


def edit_person(
    person_id: int,
    name: str | None = None,
    surname: str | None = None,
    phone_number: str | int | None = None,
    email: str | None = None,
    city: str | None = None,
    street: str | None = None,
    building: str | None = None,
    apartment: str | None = None,
) -> tuple[bool, str]:
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name, surname, contact_id, address_id
                    FROM person
                    WHERE id = %s
                    LIMIT 1;
                """, (person_id,))
                person = cursor.fetchone()
                if not person:
                    return False, "Person not found"
                old_name, old_surname, contact_id, address_id = person
                cursor.execute("""
                    SELECT phone_number, email
                    FROM contact
                    WHERE id = %s
                    LIMIT 1;
                """, (contact_id,))
                contact = cursor.fetchone()
                old_phone, old_email = contact if contact else (None, None)
                cursor.execute("""
                    SELECT city.name, address.street, address.building, address.apartment, address.coords
                    FROM address
                    JOIN city ON address.city_id = city.id
                    WHERE address.id = %s;
                """, (address_id,))
                address = cursor.fetchone()
                old_city, old_street, old_building, old_apartment, old_coords = (
                    address if address else (None, None, None, None, None)
                )
                update_person(cursor, person_id,
                              name=name if name is not None else old_name,
                              surname=surname if surname is not None else old_surname)
                new_phone = phone_number if phone_number is not None else old_phone
                new_email = email if email is not None else old_email
                if (new_phone != old_phone) or (new_email != old_email):
                    cursor.execute("""
                        UPDATE contact
                        SET phone_number = %s,
                            email = %s
                        WHERE id = %s;
                    """, (new_phone, new_email, contact_id))
                if city is not None:
                    city_id = fetch_city_id(city)
                    if city_id is None:
                        city_id = insert_city(cursor, city)
                    try:
                        coords = list(scrape_coords(city))
                    except Exception:
                        coords = old_coords
                else:
                    city_id = fetch_city_id(old_city)
                    coords = old_coords
                cursor.execute("""
                    UPDATE address
                    SET city_id = %s,
                        street = %s,
                        building = %s,
                        apartment = %s,
                        coords = %s
                    WHERE id = %s;
                """, (
                    city_id,
                    street if street is not None else old_street,
                    building if building is not None else old_building,
                    apartment if apartment is not None else old_apartment,
                    coords,
                    address_id
                ))
        return True, "Person updated successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"
    except Exception as e:
        return False, str(e)


def get_person_info(person_id: int) -> dict | None:
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, account_id, name, surname, contact_id, address_id, role
                FROM person
                WHERE id = %s
                LIMIT 1;
            """, (person_id,))
            person = cursor.fetchone()
            if not person:
                return None
            person_dict = {
                "id": person[0],
                "account_id": person[1],
                "name": person[2],
                "surname": person[3],
                "contact_id": person[4],
                "address_id": person[5],
                "role": person[6]
            }
            contact_id = person_dict["contact_id"]
            if contact_id:
                cursor.execute("SELECT phone_number, email FROM contact WHERE id = %s", (contact_id,))
                contact = cursor.fetchone()
                if contact:
                    person_dict["phone_number"], person_dict["email"] = contact
                else:
                    person_dict["phone_number"], person_dict["email"] = None, None
            else:
                person_dict["phone_number"], person_dict["email"] = None, None
            address_id = person_dict["address_id"]
            if address_id:
                cursor.execute("""
                    SELECT city.name, address.street, address.building, address.apartment, address.coords
                    FROM address
                    JOIN city ON address.city_id = city.id
                    WHERE address.id = %s;
                """, (address_id,))
                addr = cursor.fetchone()
                if addr:
                    person_dict["city"], person_dict["street"], person_dict["building"], person_dict["apartment"], person_dict["coords"] = addr
                else:
                    person_dict["city"], person_dict["street"], person_dict["building"], person_dict["apartment"], person_dict["coords"] = (None, None, None, None, None)
            else:
                person_dict["city"], person_dict["street"], person_dict["building"], person_dict["apartment"], person_dict["coords"] = (None, None, None, None, None)
            return person_dict
    except Exception as e:
        print(f"Error fetching person info: {e}")
        return None


def delete_person(person_id: int) -> tuple[bool, str]:
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT contact_id, address_id FROM person WHERE id = %s", (person_id,))
                result = cursor.fetchone()
                if not result:
                    return False, "Person not found"
                contact_id, address_id = result

                cursor.execute("DELETE FROM person WHERE id = %s", (person_id,))
                if contact_id:
                    cursor.execute("DELETE FROM contact WHERE id = %s", (contact_id,))
                if address_id:
                    cursor.execute("DELETE FROM address WHERE id = %s", (address_id,))

        return True, "Person deleted successfully"
    except Exception as e:
        return False, f"Failed to delete person: {str(e)}"


# CRUD - Books

def add_book(
    title: str,
    author: str,
    isbn_13: str | None = None,
    publisher: str | None = None,
    genre: str | None = None
) -> tuple[bool, str]:
    if not title or not author:
        return False, "Title and Author are required"
    try:
        with connection:
            with connection.cursor() as cursor:
                book_id = insert_book(cursor, title, author, isbn_13, publisher, genre)
        return True, "Book added successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"


def edit_book(
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    isbn_13: str | None = None,
    publisher: str | None = None,
    genre: str | None = None
) -> tuple[bool, str]:
    try:
        book = fetch_book(book_id)
        if not book:
            return False, "Book not found"

        update_book(
            cursor,
            book_id,
            title=title or book[1],
            author=author or book[2],
            isbn_13=isbn_13 or book[3],
            publisher=publisher or book[4],
            genre=genre or book[5]
        )
        connection.commit()
        return True, "Book updated successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"


def get_book_info(book_id: int) -> dict | None:
    try:
        with connection.cursor() as cursor:
            book = fetch_book(book_id)
            if not book:
                return None
            return {
                "id": book[0],
                "title": book[1],
                "author": book[2],
                "isbn_13": book[3],
                "publisher": book[4],
                "genre": book[5]
            }
    except Exception as e:
        print(f"Error fetching book info: {e}")
        return None

def delete_book(book_id: int) -> tuple[bool, str]:
    book = fetch_book(book_id)
    if not book:
        return False, "Book not found"
    try:
        with connection:
            with connection.cursor() as cursor:
                query = "DELETE FROM book WHERE id = %s;"
                cursor.execute(query, (book_id,))
        return True, "Book deleted successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"


# CRUD - Libraries

def add_library(
    name: str,
    city: str | None = None,
    street: str | None = None,
    building: str | None = None,
    apartment: str | None = None,
    phone_number: str | None = None,
    email: str | None = None
) -> tuple[bool, str]:
    if not name:
        return False, "Library name is required"
    try:
        with connection:
            with connection.cursor() as cursor:
                city_id = fetch_city_id(city)
                if city and city_id is None:
                    city_id = insert_city(cursor, city)
                coords = None
                if city:
                    try:
                        coords = scrape_coords(city)
                    except Exception:
                        coords = None
                contact_id = insert_contact(cursor, phone_number, email)
                address_id = insert_address(cursor, city_id, street, building, apartment, coords)

                cursor.execute("""
                    INSERT INTO library (name, address_id, contact_id, city_id)
                    VALUES (%s, %s, %s, %s)
                """, (name, address_id, contact_id, city_id))

        return True, "Library added successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"


def edit_library(
    library_id: int,
    name: str | None = None,
    city: str | None = None,
    street: str | None = None,
    building: str | None = None,
    apartment: str | None = None,
    phone_number: str | None = None,
    email: str | None = None
) -> tuple[bool, str]:
    library = fetch_library(library_id)
    if not library:
        return False, "Library not found"
    lib_id, old_name, address_id, contact_id, old_city_id = library
    old_city, old_street, old_building, old_apartment, old_coords = fetch_address(address_id)
    try:
        with connection:
            with connection.cursor() as cursor:
                if city:
                    city_id = fetch_city_id(city)
                    if city_id is None:
                        city_id = insert_city(cursor, city)
                    try:
                        coords = scrape_coords(city)
                    except Exception:
                        coords = old_coords
                else:
                    city_id = old_city_id
                    coords = old_coords
                update_library(
                    cursor,
                    library_id,
                    name=name or old_name,
                    city_id=city_id,
                    address_id=address_id
                )
                old_phone, old_email = fetch_contact(contact_id) if contact_id else (None, None)
                new_phone, new_email = phone_number or old_phone, email or old_email
                if contact_id:
                    cursor.execute("UPDATE contact SET phone_number = %s, email = %s WHERE id = %s",
                                   (new_phone, new_email, contact_id))
                cursor.execute("""
                               UPDATE address
                               SET city_id = %s,
                                   street = %s,
                                   building = %s,
                                   apartment = %s,
                                   coords = %s
                               WHERE id = %s
                               """, (
                                   city_id,
                                   street or old_street,
                                   building or old_building,
                                   apartment or old_apartment,
                                   coords,
                                   address_id
                               ))
        return True, "Library updated successfully"
    except psycopg2.Error as e:
        connection.rollback()
        return False, f"Database error: {e.pgerror}"


def get_library_info(library_id: int) -> dict | None:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, address_id, contact_id, city_id FROM library WHERE id = %s", (library_id,))
            library = cursor.fetchone()
            if not library:
                return None
            lib_dict = {
                "id": library[0],
                "name": library[1],
                "address_id": library[2],
                "contact_id": library[3],
                "city_id": library[4]
            }
            if lib_dict["contact_id"]:
                cursor.execute("SELECT phone_number, email FROM contact WHERE id = %s", (lib_dict["contact_id"],))
                contact = cursor.fetchone()
                lib_dict["phone_number"], lib_dict["email"] = contact if contact else (None, None)
            else:
                lib_dict["phone_number"], lib_dict["email"] = None, None
            if lib_dict["address_id"]:
                cursor.execute("""
                    SELECT city.name, address.street, address.building, address.apartment, address.coords
                    FROM address
                    JOIN city ON address.city_id = city.id
                    WHERE address.id = %s
                """, (lib_dict["address_id"],))
                addr = cursor.fetchone()
                lib_dict["city"], lib_dict["street"], lib_dict["building"], lib_dict["apartment"], lib_dict["coords"] = addr if addr else (None, None, None, None, None)
            else:
                lib_dict["city"], lib_dict["street"], lib_dict["building"], lib_dict["apartment"], lib_dict["coords"] = (None, None, None, None, None)
            return lib_dict
    except Exception as e:
        print(f"Error fetching library info: {e}")
        return None


def delete_library(library_id: int) -> tuple[bool, str]:
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT address_id, contact_id FROM library WHERE id = %s", (library_id,))
                result = cursor.fetchone()
                if not result:
                    return False, "Library not found"
                address_id, contact_id = result
                cursor.execute("DELETE FROM library WHERE id = %s", (library_id,))
                if contact_id:
                    cursor.execute("DELETE FROM contact WHERE id = %s", (contact_id,))
                if address_id:
                    cursor.execute("DELETE FROM address WHERE id = %s", (address_id,))
        return True, "Library deleted successfully"
    except Exception as e:
        return False, f"Failed to delete library: {str(e)}"

def assign_client_to_library(person_id, library_id) -> tuple[bool, str]:
    try:
        with connection:
            with connection.cursor() as cursor:
                insert_assignment_client_library(cursor, person_id, library_id)
        return True, "Registered"
    except Exception as e:
        return False, str(e)

def assign_employee_to_library(person_id, library_id) -> tuple[bool, str]:
    try:
        with connection:
            with connection.cursor() as cursor:
                insert_assignment_employee_library(cursor, person_id, library_id)
        return True, "Registered"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("Running controller.py")