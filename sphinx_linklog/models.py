from pydantic import BaseModel, HttpUrl
from pydantic.fields import computed_field


class LinkModel(BaseModel):
    """An edge in the graph."""

    source: HttpUrl
    target: HttpUrl
    context: str | None = None
    project: str

    @computed_field
    def target_project(self):
        """Target project."""
        path = self.target.path
        if not path:
            return ""
        return path.split()[1]
