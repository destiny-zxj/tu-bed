from sqlmodel import SQLModel


class ApiKeyCreateItem(SQLModel):
    name: str
