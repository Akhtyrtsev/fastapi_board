from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from src.auth.router import router as auth_router
from src.board.router import router as board_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

origins = ['*']

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(board_router)
app.include_router(auth_router)

