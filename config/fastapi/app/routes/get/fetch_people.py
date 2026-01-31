from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...funcs.crud_people import fetch_people_data
from ...database import get_db
from pydantic import BaseModel

router_fetch_people = APIRouter()

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
@router_fetch_people.get("/get_people")
async def get_users(db: Session = Depends(get_db)):
    try:
        users = fetch_people_data(db)

        return {"status": "success", "users": users}

    except Exception as e:
        print(f"Błąd podczas get_users: {str(e)}")
        return {"error": str(e)}