from fastapi import FastAPI
from .routes.static_content import router
from .routes.fetchers.fetch_users import router_fetch_users
from .routes.inserters.insert_user import router_insert_user
from .routes.inserters.create_account import router_create_account
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
app.include_router(router_fetch_users, prefix="/app")
app.include_router(router_insert_user, prefix="/app")
app.include_router(router_create_account, prefix="/app")