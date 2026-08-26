from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
