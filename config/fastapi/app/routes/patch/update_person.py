from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...funcs.crud_people import edit_person
from pydantic import BaseModel

router_update_person = APIRouter()

class PersonData(BaseModel):
    email: str | None = None
    name: str | None = None
    surname: str | None = None
    phone_number: int | None = None
    city: str | None = None
    street: str | None = None
    building: str | None = None
    apartment: str | None = None

@router_update_person.patch("/edit_person")
async def update_person(person_id: int, account_id: int, updated_data: PersonData, db: Session = Depends(get_db)):
    try:
        update_dict = updated_data.model_dump(exclude_unset=True)
        result = edit_person(db=db, person_id=person_id, account_id=account_id, **update_dict)

        if not result.get("success"):
            return {"error": result.get("message")}

        db.commit()
        return {"status": "success", "person_id": person_id}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}