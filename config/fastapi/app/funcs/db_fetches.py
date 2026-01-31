from sqlalchemy import text
from sqlalchemy.orm import Session

def fetch_city_id(db: Session, name: str) -> int | None:
    if not name: return None
    query = text("SELECT id FROM city WHERE name = :name LIMIT 1;")
    result = db.execute(query, {"name": name}).fetchone()
    return result[0] if result else None