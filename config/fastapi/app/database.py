from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.fastapi.app.settings import db_name, db_user, db_password

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@postgis:5432/{db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()