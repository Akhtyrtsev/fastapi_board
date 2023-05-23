from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum
from passlib.context import CryptContext

import enum

from src.db import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RolesEnum(enum.Enum):
    admin = "admin"
    manager = "manager"


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(Enum(RolesEnum))


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    role_id = Column(Integer, ForeignKey(Role.id), default=2)
    role = relationship("Role", backref="users")
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), onupdate=func.now())



