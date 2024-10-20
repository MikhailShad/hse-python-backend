from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, Field


@dataclass
class Item:
    id: int = None
    name: str = None
    price: float = None
    deleted: bool = None


@dataclass
class Cart:
    @dataclass(slots=True)
    class Item:
        id: int = None
        name: str = None
        quantity: int = None
        available: bool = None

    id: int = None
    items: List[Item] = None
    price: float = None


@dataclass
class ItemPutRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Name must be at least 1 character long")
    price: float = Field(..., ge=0, description="Price must be non-negative")

    class Config:
        extra = "forbid"


@dataclass
class ItemPatchRequest(BaseModel):
    name: str = Field(None, min_length=1, description="Name must be at least 1 character long")
    price: float = Field(None, ge=0, description="Price must be non-negative")

    class Config:
        extra = "forbid"
