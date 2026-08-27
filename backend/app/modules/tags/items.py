from sqlmodel import SQLModel


class TagCreateItem(SQLModel):
    name: str


class TagUpdateItem(SQLModel):
    name: str


class ImageTagsUpdateItem(SQLModel):
    tag_ids: list[int] = []