import re


def is_valid_email(email: str) -> bool:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return bool(EMAIL_REGEX.fullmatch(email))


def is_valid_phone_number(phone_number:int) -> bool:
    if (len(str(phone_number)) == 9 or len(str(phone_number)) == 11)  and isinstance(phone_number, int):
        return True
    else:
        return False