from fastapi import FastAPI
from .routes.static_content import router

from .routes.delete.remove_person import router_person_delete

from .routes.get.fetch_users import router_fetch_users
from .routes.get.fetch_people import router_fetch_people

from .routes.patch.update_person import router_update_person

from .routes.post.insert_user import router_insert_user
from .routes.post.insert_person import router_insert_person
from .routes.post.create_account import router_create_account

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
app.include_router(router_person_delete, prefix="/app")
app.include_router(router_fetch_users, prefix="/app")
app.include_router(router_fetch_people, prefix="/app")
app.include_router(router_update_person, prefix="/app")
app.include_router(router_insert_user, prefix="/app")
app.include_router(router_insert_person, prefix="/app")
app.include_router(router_create_account, prefix="/app")