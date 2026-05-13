"""Data model."""

from pydantic import BaseModel, HttpUrl


class LinkModel(BaseModel):
    """An edge in the graph."""

    source: HttpUrl
    target: HttpUrl
    context: str | None = None
    project: str
