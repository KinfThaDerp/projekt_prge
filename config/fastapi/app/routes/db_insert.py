from fastapi import APIRouter
from sqlalchemy import create_engine, text
from pydantic import BaseModel
from ..settings import db_name, db_user, db_password

router_insert = APIRouter()

def connect_to_db(db_name:str, db_user:str, db_password:str):
    return create_engine(
        f"postgresql://{db_user}:{db_password}@postgis:5432/{db_name}"
    )

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
async def insert_user(user: UserData):

    try:
        lat, lon = get_Coordinates(user.location)
    except Exception as e:
        print(f' Błąd podczas get_Coordinates')
        return {"error": str(e)}

    try:
        db_connection = connect_to_db(db_user=db_user, db_password=db_password, db_name=db_name)

#TODO TO DO ZROBIENIA DYNAMICZNIE

        params = {
            "name": user.name,
            "posts": user.posts,
            "location": user.location,
            "longitude": lon,
            "latitude": lat
        }

        sql_query = text("""
                    insert into users (name, posts, location, coords)
                    values (:name, :posts, :location, ST_MakePoint(:longitude, :latitude));
                    """)

        with db_connection.connect() as conn:
            result = conn.execute(sql_query, params)
            conn.commit()
            return {"status": "success"}

    except Exception as e:
        print(f' Błąd podczas insert_user')
        return {"error": str(e)}
    # return {"db_name": db_name, "db_user": user.name, "db_password": db_password}


