from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router_get_users = APIRouter()

@router_get_users.get("/get_users")
async def get_users(db: Session = Depends(get_db)):
    try:
        sql_query = text("""SELECT * FROM users""")

        result = db.execute(sql_query)

        users = [dict(row._mapping) for row in result]

        return {"status": "success", "users": users}

    except Exception as e:
        print(f"Błąd podczas get_users: {str(e)}")
        return {"error": str(e)}