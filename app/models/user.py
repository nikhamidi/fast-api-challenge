"""User models."""

from datetime import datetime
from typing import Annotated, Any, Optional

from beanie import Document
from pydantic import BaseModel




class UserOut(BaseModel):
    username : str

class UserAuth(UserOut):
    password: str

class User(Document, UserAuth):
    @property
    def created(self) -> datetime | None:
        return self.id.generation_time if self.id else None

    @property
    def jwt_subject(self) -> dict[str, Any]:
        return {"username": self.username}

    @classmethod
    async def by_username(cls, username: str) -> Optional["User"]:
        return await cls.find_one(cls.username == username)
