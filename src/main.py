import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from src.auth.schema import User as SchemaUser
from src.auth.schema import User
from src.auth.models import User as ModelUser

from src.auth.router import router as auth_router
import os

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/users/')
async def users():
    users_query = db.session.query(ModelUser).all()
    return users_query

