from sqlmodel import SQLModel


class DashboardStats(SQLModel):
    total_users: int
    total_images: int
    total_storage_bytes: int
