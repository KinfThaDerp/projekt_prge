from sqlalchemy import text
from sqlalchemy.orm import Session

def fetch_city_id(db: Session, name: str) -> int | None:
    if not name: return None
    query = text("SELECT id FROM city WHERE name = :name LIMIT 1;")
    result = db.execute(query, {"name": name}).fetchone()
    return result[0] if result else None

def fetch_city(db: Session, person_id: int) -> str | None:
    query = text("""
            SELECT city.name
            FROM person JOIN address ON person.address_id = address.id JOIN city ON address.city_id = city.id
            WHERE person.id = :p_id
            LIMIT 1; \
            """)
    result = db.execute(query, {"p_id": person_id}).fetchone()
    return result[0] if result else None

def fetch_city_name(db: Session, city_id: int) -> str | None:
    query = text("SELECT name FROM city WHERE id = :c_id LIMIT 1;")
    result = db.execute(query, {"c_id": city_id}).fetchone()
    return result[0] if result else None

def fetch_all_city_names(db: Session) -> list[str]:
    query = text("SELECT DISTINCT name FROM city ORDER BY name;")
    result = db.execute(query)
    rows = result.fetchall()
    return [row[0] for row in rows]


def fetch_address(db: Session, address_id: int | None) -> dict | None:
    if not address_id: return None
    query = text("""
            SELECT city.name as city_name, address.street, address.building, address.apartment
            FROM address
            JOIN city ON address.city_id = city.id
            WHERE address.id = :add_id;
            """)
    result = db.execute(query, {"add_id": address_id}).fetchone()
    return dict(result._mapping) if result else None


def fetch_contact(db: Session, contact_id: int):
    if not contact_id: return None
    query =text("""
               SELECT phone_number, email 
               FROM contact 
               WHERE id = :con_id
                """)
    result = db.execute(query, {"con_id": contact_id }).fetchone()
    return dict(result._mapping) if result else None
