import uvicorn
from fastapi import FastAPI, Depends
from fastapi_sqlalchemy import DBSessionMiddleware, db

from src.auth.schema import User as SchemaUser
from src.auth.schema import User
from src.auth.models import User as ModelUser

from src.auth.router import router as auth_router
from src.auth.dependencies import RoleChecker
import os

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

admin_permission = RoleChecker(["admin"])


@app.get('/users/', dependencies=[Depends(admin_permission)],)
async def users():
    users_query = db.session.query(ModelUser).all()
    return users_query

