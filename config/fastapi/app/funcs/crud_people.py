from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text, create_engine
from .db_fetches import fetch_city_id
from .db_inserts import insert_city
from .scrapers import scrape_coordinates


def insert_person(
    db: Session,
    account_id: int,
    name: str,
    surname: str,
    contact_id: int | None,
    address_id: int | None,
    role: str = 'client'
) -> dict:
    query = text("""
            INSERT INTO person (account_id, name, surname, contact_id, address_id, role)
            VALUES (:acc_id, :name, :surname, :c_id, :add_id, :role)
            RETURNING id;
            """)
    result = db.execute(query, {
        "acc_id": account_id,
        "name": name,
        "surname": surname,
        "c_id": contact_id,
        "add_id": address_id,
        "role": role
    })
    person_id = result.fetchone()[0]
    return person_id

def fetch_people_basic(db: Session, role: str | None = None) -> dict:
    query_str = "SELECT id, account_id, name, surname, contact_id, address_id, role FROM person"

    if role:
        query_str += " WHERE role = :role"
        result = db.execute(text(query_str), {"role": role})
    else:
        result = db.execute(text(query_str))
    users_basic = [dict(row._mapping) for row in result]
    return {"success": True, "users_basic": users_basic}


def fetch_people_data(db: Session, role: str | None = None) -> dict:
    from .db_fetches import fetch_contact, fetch_address
    users_basic = fetch_people_basic(db, role)
    users_data = []

    for user in users_basic:
        contact_data = fetch_contact(db, user.get("contact_id"))
        address_data = fetch_address(db, user.get("address_id"))

        user_data = {
            "id": user["id"],
            "account_id": user["account_id"],
            "name": user["name"],
            "surname": user["surname"],
            "role": user["role"],
            "contact_data": contact_data,
            "address_data": address_data
        }

        users_data.append(user_data)
    return {"success": True, "users":users_data}




def edit_person(db: Session, person_id: int, **kwargs) -> dict:
    if not kwargs:
        return {"success": False, "message": "No data provided for update"}

    # 1. Fetch current links to other tables
    find_ids_query = text("SELECT contact_id, address_id FROM person WHERE id = :p_id")
    person_record = db.execute(find_ids_query, {"p_id": person_id}).fetchone()

    if not person_record:
        return {"success": False, "message": f"Person {person_id} not found"}

    contact_id = person_record._mapping["contact_id"]
    address_id = person_record._mapping["address_id"]

    # 2. Update Person table (name, surname)
    person_updates = {k: v for k, v in kwargs.items() if k in ['name', 'surname']}
    if person_updates:
        set_clause = ", ".join([f"{k} = :{k}" for k in person_updates])
        db.execute(
            text(f"UPDATE person SET {set_clause} WHERE id = :p_id"),
            {**person_updates, "p_id": person_id}
        )

    # 3. Update Contact table (email, phone_number)
    contact_updates = {k: v for k, v in kwargs.items() if k in ['email', 'phone_number']}
    if contact_updates and contact_id:
        # Use phone_number as the key to match database column
        set_clause = ", ".join([f"{k} = :{k}" for k in contact_updates.keys()])
        db.execute(
            text(f"UPDATE contact SET {set_clause} WHERE id = :c_id"),
            {**contact_updates, "c_id": contact_id}
        )

    # 4. Update Address and City
    address_updates = {k: v for k, v in kwargs.items() if k in ['street', 'building', 'apartment']}
    new_city_name = kwargs.get('city')

    if (address_updates or new_city_name) and address_id:
        params = {**address_updates, "a_id": address_id}
        update_parts = []

        # Add standard address fields to update list
        for key in address_updates:
            update_parts.append(f"{key} = :{key}")

        # Handle City Change logic
        if new_city_name:
            city_id = fetch_city_id(db, new_city_name)
            if not city_id:
                city_id = insert_city(db, new_city_name)

            coords = scrape_coordinates(new_city_name)
            lat, lon = (coords.get("lat"), coords.get("lon")) if "error" not in coords else (None, None)

            params.update({"city_id": city_id, "lat": lat, "lon": lon})

            update_parts.append("city_id = :city_id")
            update_parts.append("""
                coords = CASE 
                    WHEN :lat IS NOT NULL AND :lon IS NOT NULL 
                    THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) 
                    ELSE coords 
                END
            """)

        # Join all parts with a single comma to avoid syntax errors
        if update_parts:
            full_set_clause = ", ".join(update_parts)
            db.execute(
                text(f"UPDATE address SET {full_set_clause} WHERE id = :a_id"),
                params
            )

    return {"success": True, "message": f"Person {person_id} updated successfully"}



def delete_person(db: Session, person_id: int):
    find_ids_query = text("SELECT contact_id, address_id FROM person WHERE id = :p_id")
    result = db.execute(find_ids_query, {"p_id": person_id}).fetchone()
    if not result:
        return {"success": False, "message": "Person not found"}

    contact_id = result._mapping["contact_id"]
    address_id = result._mapping["address_id"]

    db.execute(text("DELETE FROM person WHERE id = :p_id"), {"p_id": person_id})
    if contact_id: db.execute(text("DELETE FROM contact WHERE id = :c_id"), {"c_id": contact_id})
    if address_id: db.execute(text("DELETE FROM address WHERE id = :a_id"), {"a_id": address_id})

    return {"success": True, "message": "Person data deleted"}



def fetch_employee_library_info(db: Session, person_id: int):
    query = text("""
            SELECT l.id, l.name 
            FROM library l
            JOIN library_employee le ON l.id = le.library_id
            WHERE le.person_id = %p_id
            LIMIT 1;
            """)
    result = db.execute(query, {"p_id": person_id }).fetchone()
    data = dict(result._mapping) if result else None

    if data:
        return {
            "success": True,
            "library_data": data
        }
    return {"success": False}



if __name__ == "__main__":
    SQLALCHEMY_DATABASE_URL = f"postgresql://admin:admin@localhost:5444/prge_bgm"

    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    db_gen = get_db()
    try:
        db_session = next(db_gen)

        users = fetch_people_data(db_session)

        for user in users:
            print(user)

    except StopIteration:
        print("Database generator failed to yield a session.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db_gen.close()