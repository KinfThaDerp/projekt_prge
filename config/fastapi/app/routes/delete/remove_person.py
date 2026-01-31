from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...funcs.crud_people import delete_person
from pydantic import BaseModel

class del_inf(BaseModel):
    account_id: int
    person_id: int


router_person_delete = APIRouter()

@router_person_delete.delete("/delete_person")
async def delete_person_point(info: del_inf, db: Session = Depends(get_db)):
    try:
        delete_person(db, info.person_id)

        db.commit()
        return {"status": "success", "message": f"Person {info.person_id} deleted"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}