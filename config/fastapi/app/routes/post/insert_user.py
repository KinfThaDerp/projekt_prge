from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...database import get_db
from ...funcs.scrapers import scrape_coordinates
from pydantic import BaseModel

router_insert_user = APIRouter()

class UserData(BaseModel):
    name: str
    posts: int
    location: str

@router_insert_user.post("/insert_user")
async def insert_user(user: UserData, db: Session = Depends(get_db)):

    coords = scrape_coordinates(user.location)
    if not coords.get("success"):
        return {"error": f"Coord error: {coords.get('error', 'Unknown error')}"}

    lat = coords["lat"]
    lon = coords["lon"]

    try:
        params = {
            "name": user.name,
            "posts": user.posts,
            "location": user.location,
            "longitude": lon,
            "latitude": lat
        }

        sql_query = text("""
                         INSERT INTO users (name, posts, location, coords)
                         VALUES (:name, :posts, :location, ST_MakePoint(:longitude, :latitude));
                         """)

        db.execute(sql_query, params)
        db.commit()

        return {"status": "success"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}


if __name__ == "__main__":
    print(scrape_coordinates("Legionowo"))