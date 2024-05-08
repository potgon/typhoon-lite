import os
from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from api.main import api_router

load_dotenv()

app = FastAPI(title="Typhoon")

register_tortoise(
    app,
    db_url=os.getenv("DB_URL"),
    modules={"models": ["database.models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)

app.include_router(api_router, prefix=os.getenv("API_V1_STR"))
