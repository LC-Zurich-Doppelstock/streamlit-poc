from datetime import date
from pydantic import AliasPath, BaseModel, Field
from enum import Enum


class Article(BaseModel):
    title: str = Field(validation_alias=AliasPath('properties', 'title'))
    price: float = Field(validation_alias=AliasPath('properties', 'price'))
    quantity: int = Field(validation_alias=AliasPath('properties', 'quantity'))