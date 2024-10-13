from typing import Optional

from beanie import Document ,PydanticObjectId
from pydantic import BaseModel

class StoryIn(BaseModel):
    title : str 
    content : str
    country: Optional[str] = None   

class StoryOut(StoryIn):
    id: PydanticObjectId
    author : str | None

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    country: Optional[str] = None


class Story(Document, StoryOut):

    @classmethod
    async def by_author(cls, author: str) -> Optional["Story"]:
        return await cls.find_all(cls.author == author)
