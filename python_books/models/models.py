import datetime

import bcrypt
import reflex as rx
from sqlmodel import Field


class BookList(
    rx.Model,
    table=True,
):
    title: str = Field(nullable=False)
    author: str = Field(nullable=False)
    date_read: datetime.datetime = Field(nullable=False)
    rating: int = Field(nullable=False)
    review: str = Field(nullable=False)
    num_times_read: int = Field(nullable=False)
    open_library_key: str = Field(nullable=False)


class User_Session(
    rx.Model,
    table=True,
):
    u_id: int = Field(index=True, nullable=False)
    sess_id: str = Field(unique=True, index=True, nullable=False)
    exp: datetime.datetime = Field(
        default_factory=datetime.datetime.now, nullable=False
    )


class User(
    rx.Model,
    table=True,
):
    name: str = Field(unique=True, index=True, nullable=False)
    pw_hash: bytes = Field(nullable=False)
    enabled: bool = False

    @staticmethod
    def hash_password(pw: str) -> bytes:
        bytes_password = pw.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(bytes_password, salt)

    def verify(self, pw: str) -> bool:
        bytes_password = pw.encode("utf-8")
        return bcrypt.checkpw(bytes_password, self.pw_hash)
