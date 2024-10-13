from fastapi import FastAPI

from api.v1 import auth as auth_api_v1
from db.db import connect_and_init_db, close_db_connect
from api.v1 import story as story_api_v1

app = FastAPI()

app.add_event_handler("startup", connect_and_init_db)
app.add_event_handler("shutdown", close_db_connect)

app.include_router(
    auth_api_v1.router,
    tags=["auth_v1"]
)

app.include_router(
    story_api_v1.router,
    tags=["story_v1"]
)
