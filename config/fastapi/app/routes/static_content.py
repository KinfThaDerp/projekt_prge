from fastapi import APIRouter

router = APIRouter()

@router.get("/endpoint")
async def endpoint():
    return [
        {"hello": "world"},
    ]

