from pydantic import BaseModel, validator
from typing import List, Union
from datetime import date, datetime, time, timedelta


class Profile(BaseModel):
    user_id: Union[int, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    phone_number: Union[str, None] = None
    avatar_url: Union[str, None] = None

    class Config:
        orm_mode = True


class ProfileWithId(BaseModel):
    id: int
    user_id: Union[int, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    phone_number: Union[str, None] = None
    avatar_url: Union[str, None] = None


class Project(BaseModel):
    id: int
    name: str
    description: str
    user_id: int
    created: datetime
    updated: Union[datetime, None] = None

    @validator('created', 'updated', pre=True)
    def parse_datetime(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                print(e)
                return datetime.now()
        return value

    @validator('created', 'updated', whole=True)
    def format_datetime(cls, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value


class ProjectChange(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    user_id: Union[int, None] = None

    class Config:
        orm_mode = True


class Ticket(BaseModel):
    id: int
    name: str
    description: str
    status: str
    project_id: int
    created: datetime
    updated: Union[datetime, None] = None

    @validator('created', 'updated', pre=True)
    def parse_datetime(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                print(e)
                return datetime.now()
        return value

    @validator('created', 'updated', whole=True)
    def format_datetime(cls, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value


class TicketChange(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    status: Union[str, None] = None
    project_id: Union[int, None] = None
