from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from pydantic import BaseModel

router_insert = APIRouter()

class UserData(BaseModel):
    name: str
    posts: int
    location: str

def get_Coordinates(location:str) -> list[float]:
    import requests
    from bs4 import BeautifulSoup
    headers = {
        "User-Agent": "<Mozilla 5/0 (Windows NT 10.0; Win64; x64; Trident/7.0)>",
    }
    url: str = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url, headers=headers)
    response_html = BeautifulSoup(response.content, 'html.parser')
    latitude = float((response_html.select('.latitude'))[1].text.replace(',', '.'))
    longitude = float((response_html.select('.longitude'))[1].text.replace(',', '.'))
    return [latitude, longitude]


@router_insert.post("/insert_user")
async def insert_user(user: UserData, db: Session = Depends(get_db)):
    try:
        lat, lon = get_Coordinates(user.location)
    except Exception as e:
        return {"error": f"Coord error: {str(e)}"}

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
