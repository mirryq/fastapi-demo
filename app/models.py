"""
决定表格数据长啥样
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, text
from sqlmodel import Field, SQLModel, Relationship


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    published: bool = Field(default=True, sa_column_kwargs={
                            "server_default": text("true")})
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        ),
    )
    owner_id: int | None = Field(foreign_key="users.id", ondelete="SET NULL")
    owner: list["User"] = Relationship()


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        ),
    )


class Vote(SQLModel, table=True):
    __tablename__ = "votes"
    user_id: int = Field(foreign_key="users.id",
                         ondelete="CASCADE", primary_key=True)
    post_id: int = Field(foreign_key="posts.id",
                         ondelete="CASCADE", primary_key=True)
