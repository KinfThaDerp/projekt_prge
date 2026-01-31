from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...database import get_db
from ...funcs.scrapers import scrape_coordinates
from ...funcs.validators import email_valid, email_exists
from ...funcs.db_fetches import fetch_city_id
from ...funcs.db_inserts import insert_city, insert_address, insert_contact
from ...funcs.crud_people import insert_person
from pydantic import BaseModel

router_insert_person = APIRouter()

class PersonData(BaseModel):
    account_id: int
    email: str | None = None
    name: str
    surname: str
    phone_number: int | None = None
    city: str
    street: str | None = None
    building: str | None = None
    apartment: str | None = None

@router_insert_person.post("/insert_person")
async def create_person(person: PersonData, db: Session = Depends(get_db)):
    try:
        if not email_valid(person.email):
            return {"error": "Invalid Email Format"}
        if email_exists(db, person.email):
            return {"error": "Email already exists in contact records"}

        city_id = fetch_city_id(db, person.city)
        if not city_id:
            city_id = insert_city(db, person.city)

        coords = scrape_coordinates(person.city)
        if not coords.get("success"):
            return {"error": f"Coord error: {coords.get('error', 'Unknown error')}"}

        contact_id = insert_contact(db, person.phone_number, person.email)
        address_id = insert_address(db, city_id, person.street, person.building, person.apartment, coords)

        person_id = insert_person(db, person.account_id, person.name, person.surname, contact_id, address_id)

        db.commit()

        return {
            "status": "success",
            "ids": {
                "person_id": person_id,
                "contact_id": contact_id,
                "address_id": address_id
            }
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

if __name__ == "__main__":
    print(scrape_coordinates("Legionowo"))