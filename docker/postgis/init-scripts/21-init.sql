-- coords implemented as real[2] since PostGIS is unavailable
-- CASCADE drops tables safely

DROP TABLE IF EXISTS book_copy CASCADE;
DROP TABLE IF EXISTS book CASCADE;
DROP TABLE IF EXISTS library_employee CASCADE;
DROP TABLE IF EXISTS library CASCADE;
DROP TABLE IF EXISTS person CASCADE;
DROP TABLE IF EXISTS account CASCADE;
DROP TABLE IF EXISTS address CASCADE;
DROP TABLE IF EXISTS contact CASCADE;
DROP TABLE IF EXISTS city CASCADE;


CREATE TABLE contact (
    id serial PRIMARY KEY,
    phone_number text,
    email text UNIQUE
);


CREATE TABLE city (
    id serial PRIMARY KEY,
    name text NOT NULL,
    voivodeship text NOT NULL,
    coords real[2]
);


CREATE TABLE address (
    id serial PRIMARY KEY,
    city_id INT REFERENCES city(id) ON DELETE SET NULL,
    street text NOT NULL,
    building text NOT NULL,
    apartment text,
    coords real[2]
);


CREATE TABLE account (
    id serial PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE person (
    id serial PRIMARY KEY,
    account_id INT REFERENCES account(id) ON DELETE SET NULL,
    name text NOT NULL,
    surname text NOT NULL,
    contact_id INT REFERENCES contact(id) ON DELETE SET NULL,
    address_id INT REFERENCES address(id) ON DELETE SET NULL,
    role text NOT NULL DEFAULT 'client' CHECK (role IN ('employee', 'client'))
);


CREATE TABLE library (
    id serial PRIMARY KEY,
    name text NOT NULL,
    address_id INT REFERENCES address(id) ON DELETE SET NULL,
    contact_id INT REFERENCES contact(id) ON DELETE SET NULL,
    city_id INT REFERENCES city(id) ON DELETE SET NULL
);


CREATE TABLE library_employee (
    id serial PRIMARY KEY,
    library_id INT REFERENCES library(id) ON DELETE CASCADE,
    person_id INT REFERENCES person(id) ON DELETE CASCADE,
    working_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(library_id, person_id)
);


CREATE TABLE book (
    id serial PRIMARY KEY,
    title text NOT NULL,
    author text NOT NULL,
    isbn_13 text UNIQUE,
    publisher text,
    genre text
);


CREATE TABLE book_copy (
    id serial PRIMARY KEY,
    book_id INT REFERENCES book(id) ON DELETE SET NULL,
    library_id INT REFERENCES library(id) ON DELETE SET NULL,
    barcode text,
    condition text
);


CREATE TABLE library_client (
    id serial PRIMARY KEY,
    library_id INT REFERENCES library(id) ON DELETE CASCADE,
    person_id INT REFERENCES person(id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(library_id, person_id)
);
