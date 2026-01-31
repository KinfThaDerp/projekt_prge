from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...database import get_db
from ...funcs.scrapers import scrape_coordinates
from ...funcs.crud_people import insert_person
from ...funcs.db_inserts import insert_city, insert_address, insert_contact, insert_account
from ...funcs.db_fetches import fetch_city_id
from ...funcs.validators import username_exists, email_valid, email_exists
from pydantic import BaseModel



router_create_account = APIRouter()

class AccountCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    name: str
    surname: str
    phone_number: int | None = None
    city: str
    street: str | None = None
    building: str | None = None
    apartment: str | None = None


@router_create_account.post("/create_account")
async def create_account(user: AccountCreate, db: Session = Depends(get_db)):
    try:
        if user.password != user.confirm_password:
            return {"error": "Passwords do not match"}
        if username_exists(db, user.username):
            return {"error": "Username already exists"}
        if not email_valid(user.email):
            return {"error": "Invalid Email Format"}
        if email_exists(db, user.email):
            return {"error": "Email already exists"}

        city_id = fetch_city_id(db, user.city)
        if not city_id:
            city_id = insert_city(db, user.city)

        coords = scrape_coordinates(user.city)

        account_id = insert_account(db, user.username, user.email, user.password)
        contact_id = insert_contact(db, user.phone_number, user.email)
        address_id = insert_address(db, city_id, user.street, user.building, user.apartment, coords)

        person_id = insert_person(db, account_id, user.name, user.surname, contact_id, address_id)
        db.commit()

        return {
            "status": "success",
            "ids": {
                "account_id": account_id,
                "contact_id": contact_id,
                "address_id": address_id,
                "person_id": person_id
            }
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

