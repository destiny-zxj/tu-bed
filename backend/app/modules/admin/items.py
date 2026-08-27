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


class UserListQueryItem(SQLModel):
    page: int = 1
    page_size: int = 20


class ImageBatchDeleteItem(SQLModel):
    image_ids: list[int]
