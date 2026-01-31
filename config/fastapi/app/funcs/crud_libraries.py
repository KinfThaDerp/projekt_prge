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

def update_library(cursor, library_id: int, **kwargs) -> None:
    query = """
                UPDATE library SET {} WHERE id = %s;
                """.format(
        ", ".join(f"{key} = %s" for key in kwargs.keys())
    )
    cursor.execute(query, (*kwargs.values(), library_id))

def fetch_library_client_ids(library_id: int) -> list[int]:
    query = "SELECT person_id FROM library_client WHERE library_id = %s;"
    cursor.execute(query, (library_id,))
    return [row[0] for row in cursor.fetchall()]


def fetch_library_employee_ids(library_id: int) -> list[int]:
    query = "SELECT person_id FROM library_employee WHERE library_id = %s;"
    cursor.execute(query, (library_id,))
    return [row[0] for row in cursor.fetchall()]