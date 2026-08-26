from sqlmodel import SQLModel


class LoginItem(SQLModel):
    username: str
    password: str
