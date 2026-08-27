from sqlmodel import SQLModel


class ApiKeyCreateItem(SQLModel):
    name: str


class ApiKeyListQueryItem(SQLModel):
    page: int = 1
    page_size: int = 20
