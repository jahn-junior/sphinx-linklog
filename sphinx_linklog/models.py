"""Data model."""

from pydantic import BaseModel, HttpUrl, TypeAdapter


class LinkModel(BaseModel):
    """An edge in the graph."""

    source: HttpUrl
    target: HttpUrl
    context: str | None = None
    project: str


LinkModelAdapter = TypeAdapter(list[LinkModel])
