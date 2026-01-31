from sqlalchemy import text
from sqlalchemy.orm import Session
import re


def email_valid(email: str) -> bool:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return bool(EMAIL_REGEX.fullmatch(email))


def is_valid_phone_number(phone_number:int) -> bool:
    if (len(str(phone_number)) == 9 or len(str(phone_number)) == 11)  and isinstance(phone_number, int):
        return True
    else:
        return False


def username_exists(db: Session, username: str) -> bool:
    result = db.execute(text("SELECT 1 FROM account WHERE username = :u"), {"u": username})
    return result.fetchone() is not None


def email_exists(db: Session, email: str) -> bool:
    result = db.execute(text("SELECT 1 FROM account WHERE email = :e"), {"e": email})
    return result.fetchone() is not None
