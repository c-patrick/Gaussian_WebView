from app.extensions import db
from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from flask_login import UserMixin
import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email_confirmed_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(100), server_default="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, role={self.role!r}, name={self.name!r}, email={self.email!r})"
