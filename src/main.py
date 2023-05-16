import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from src.auth.schema import User as SchemaUser
from src.auth.schema import User
from src.auth.models import User as ModelUser
import os

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/users/')
async def users():
    users_query = db.session.query(ModelUser).all()
    return users_query


@app.post('/users/', response_model=SchemaUser)
async def users(user: SchemaUser):
    db_user = ModelUser(username=user.username, email=user.email)
    db_user.set_password(user.password)
    db.session.add(db_user)
    db.session.commit()
    return db_user
