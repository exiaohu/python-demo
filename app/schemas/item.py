from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Item(ItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
