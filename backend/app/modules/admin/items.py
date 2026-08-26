from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel


class UserCreateItem(SQLModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    is_admin: bool = False


class UserUpdateItem(SQLModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
