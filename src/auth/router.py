from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schema import User as UserSchema
from src.auth.schema import Token as TokenSchema
from src.auth.schema import UserResponse
from fastapi_sqlalchemy import db
from src.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from uuid import uuid4
from src.auth.models import User as ModelUser
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth")


@router.post('/signup', summary="Create new user", response_model=UserResponse)
async def create_user(data: UserSchema):
    # querying database to check if user already exist
    user_query = db.session.query(ModelUser).filter_by(email=data.email).first()
    if user_query is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    db_user = ModelUser(username=data.username, email=data.email, password=get_hashed_password(data.password))
    db.session.add(db_user)
    db.session.commit()    # saving user to database
    user = UserResponse(username=db_user.username, email=db_user.email, id=db_user.id)
    return user


@router.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.session.query(ModelUser).filter_by(email=form_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@router.get('/me', summary='Get details of currently logged in user', response_model=UserResponse)
async def get_me(user: ModelUser = Depends(get_current_user)):
    return user