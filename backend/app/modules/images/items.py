from sqlmodel import SQLModel


class ImageListQueryItem(SQLModel):
    page: int = 1
    page_size: int = 20
