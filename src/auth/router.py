from fastapi import APIRouter, status, HTTPException, Depends
from starlette.status import HTTP_204_NO_CONTENT
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schema import User as UserSchema
from src.auth.schema import Token as TokenSchema
from src.auth.schema import UserResponse, UserUpdate
from fastapi_sqlalchemy import db
from src.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from src.auth.models import User as ModelUser
from src.auth.dependencies import get_current_user, RoleChecker, get_current_user_refresh

router = APIRouter(prefix="/auth")


@router.post('/signup', summary="Create new user", response_model=UserResponse, tags=['auth'])
async def create_user(data: UserSchema):
    # querying database to check if user already exist
    user_query = db.session.query(ModelUser).filter_by(email=data.email).first()
    if user_query is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    db_user = ModelUser(username=data.username, email=data.email, password=get_hashed_password(data.password),
                        role_id=data.role_id)
    db.session.add(db_user)
    db.session.commit()    # saving user to database
    user = UserResponse(username=db_user.username, email=db_user.email, id=db_user.id, role=db_user.role.name.value)
    return user


@router.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema, tags=['auth'])
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

allow_read_resource = RoleChecker(["admin"])


@router.get('/my_user', summary='Get details of currently logged in user', response_model=UserResponse, tags=['auth'])
async def get_me(user: ModelUser = Depends(get_current_user)):
    return user


@router.get('/refresh', summary='Get tokens using refresh token', tags=['auth'])
async def refresh(user: ModelUser = Depends(get_current_user_refresh)):
    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@router.patch('/my_user', summary='Patch current user', tags=['auth'])
async def patch_user(data: UserUpdate, user: ModelUser = Depends(get_current_user)):
    update_data = data.dict(exclude_unset=True)
    updated_item = user.copy(update=update_data)
    to_update = updated_item.dict()
    to_update.pop("role")
    if to_update.get("password"):
        to_update["password"] = get_hashed_password(to_update["password"])
    db.session.query(ModelUser).filter_by(id=user.id).update(to_update, synchronize_session=False)
    db.session.commit()
    access_token = create_access_token(to_update.get('email'))
    refresh_token = create_refresh_token(to_update.get('email'))
    response = UserResponse(**to_update, role=user.role).dict()
    response['access_token'] = access_token
    response['refresh_token'] = refresh_token
    return response


@router.delete("/my_user", status_code=HTTP_204_NO_CONTENT, tags=['auth'])
def delete_user(user: ModelUser = Depends(get_current_user)):
    db_user = db.session.query(ModelUser).filter_by(id=user.id).first()
    db.session.delete(db_user)
    db.session.commit()
    return None
