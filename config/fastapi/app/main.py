from fastapi import FastAPI
from app.routes.static_content import router
from app.routes.db_insert import router_insert
from app.routes.dynamic_content import router_get_users
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="Mapbook API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/app")
app.include_router(router_insert, prefix="/app")
app.include_router(router_get_users, prefix="/app")