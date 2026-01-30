-- ========================================
-- Sample Data Insertion for Library System
-- ========================================

-- =========================
-- Cities
-- =========================
INSERT INTO city (name, voivodeship, coords) VALUES
('Warsaw', 'Mazowieckie', ARRAY[52.2297, 21.0122]::real[]),
('Krakow', 'Malopolskie', ARRAY[50.0647, 19.9450]::real[]),
('Gdansk', 'Pomorskie', ARRAY[54.3520, 18.6466]::real[]);


-- =========================
-- Addresses
-- =========================
INSERT INTO address (city_id, street, building, apartment, coords) VALUES
(1, 'Marszalkowska', '10', '5A', ARRAY[52.2297, 21.0122]::real[]),
(2, 'Florianska', '15', NULL, ARRAY[50.0647, 19.9450]::real[]),
(3, 'Dluga', '8', '2B', ARRAY[54.3520, 18.6466]::real[]),
(1, 'Nowy Swiat', '20', '3C', ARRAY[52.2300, 21.0100]::real[]);


-- =========================
-- Contacts
-- =========================
INSERT INTO contact (phone_number, email) VALUES
('123456789', 'warsaw.library@example.com'),
('987654321', 'krakow.library@example.com'),
('555666777', 'gdansk.library@example.com'),
('111222333', 'client1@example.com'),
('444555666', 'employee1@example.com');


-- =========================
-- Accounts
-- =========================
INSERT INTO account (username, email, password_hash) VALUES
('client1', 'client1@example.com', '$2b$12$EXAMPLEHASH1'),
('client2', 'client2@example.com', '$2b$12$EXAMPLEHASH2'),
('employee1', 'employee1@example.com', '$2b$12$EXAMPLEHASH3'),
('employee2', 'employee2@example.com', '$2b$12$EXAMPLEHASH4');


-- =========================
-- People
-- =========================
-- Clients
INSERT INTO person (account_id, name, surname, contact_id, address_id, role) VALUES
(1, 'Anna', 'Nowak', 4, 1, 'client'),
(2, 'Piotr', 'Kowalski', NULL, 2, 'client');

-- Employees
INSERT INTO person (account_id, name, surname, contact_id, address_id, role) VALUES
(3, 'Marek', 'Lewandowski', 5, 3, 'employee'),
(4, 'Ewa', 'Malinowska', NULL, 4, 'employee');


-- =========================
-- Libraries
-- =========================
INSERT INTO library (name, address_id, contact_id, city_id) VALUES
('Central Library Warsaw', 1, 1, 1),
('Krakow City Library', 2, 2, 2),
('Gdansk Public Library', 3, 3, 3);


-- =========================
-- Library Employees
-- =========================
INSERT INTO library_employee (library_id, person_id) VALUES
(1, 3),
(2, 4);


-- =========================
-- Library Clients
-- =========================
INSERT INTO library_client (library_id, person_id) VALUES
(1, 1),
(2, 2);


-- =========================
-- Books
-- =========================
INSERT INTO book (title, author, isbn_13, publisher, genre) VALUES
('Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', '9780747532699', 'Bloomsbury', 'Fantasy'),
('The Hobbit', 'J.R.R. Tolkien', '9780261103344', 'Allen & Unwin', 'Fantasy'),
('Clean Code', 'Robert C. Martin', '9780132350884', 'Prentice Hall', 'Programming');


-- =========================
-- Book Copies
-- =========================
INSERT INTO book_copy (book_id, library_id, barcode, condition) VALUES
(1, 1, 'BC0001', 'New'),
(1, 2, 'BC0002', 'Good'),
(2, 1, 'BC0003', 'Worn'),
(3, 3, 'BC0004', 'New');

