from sqlalchemy import text
from sqlalchemy.orm import Session
from .security import hash_password
from .scrapers import scrape_coordinates, scrape_voivodeship


def insert_account(db: Session, username: str, email: str, password: str) -> int:
    password_hash = hash_password(password)
    query = text("""
                 INSERT INTO account (username, email, password_hash)
                 VALUES (:username, :email, :pw_hash)
                 RETURNING id;
                 """)
    result = db.execute(query, {
        "username": username,
        "email": email,
        "pw_hash": password_hash
    })
    account_id = result.fetchone()[0]
    return account_id


def insert_contact(db: Session, phone_number: int | None, email: str | None ) -> int:
    query = text("""
            INSERT INTO contact (phone_number, email)
            VALUES (:ph_n, :email)
            RETURNING id;
            """)
    result = db.execute(query, {
        "ph_n": phone_number,
        "email": email
    })
    contact_id = result.fetchone()[0]
    return contact_id


def insert_address(
    db: Session,
    city_id: int | None,
    street: str | None,
    building: str | None,
    apartment: str | None,
    coords: dict | None
) -> int:
    if "error" in coords:
        lat, lon = None, None
    else:
        lat, lon = coords["lat"], coords["lon"]

    query = text("""
            INSERT INTO address (city_id, street, building, apartment, coords)
            VALUES (:c_id, :street, :building, :apartment, 
               CASE 
                    WHEN :lat IS NOT NULL AND :lon IS NOT NULL 
                    THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) 
                END)
            RETURNING id;
            """)
    result = db.execute(query, {
        "c_id": city_id,
        "street": street,
        "building": building,
        "apartment": apartment,
        "coords": coords,
        "lat": lat,
        "lon": lon
    })
    address_id = result.fetchone()[0]
    return address_id





def insert_city(db: Session, name: str) -> int | None:
    if not name:
        return None

    voivodeship = scrape_voivodeship(name) or "Unknown"

    coords = scrape_coordinates(name)
    if "error" in coords:
        lat, lon = None, None
    else:
        lat, lon = coords["lat"], coords["lon"]

    query = text("""
                 INSERT INTO city (name, voivodeship, coords)
                 VALUES (:name, :voivodeship, 
                        CASE 
                            WHEN :lat IS NOT NULL AND :lon IS NOT NULL 
                            THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) 
                        END)
                 RETURNING id;
                 """)

    result = db.execute(query, {
        "name": name,
        "voivodeship": voivodeship,
        "lon": lon,
        "lat": lat
    })
    city_id = result.fetchone()[0]
    return city_id

