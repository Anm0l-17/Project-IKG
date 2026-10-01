from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceBase(BaseModel):
    name: str
    domain: str
    rss_url: str | None = None
    language: str = "en"
    country: str = "IN"
    trust_score: float = 1.0
    logo_url: str | None = None
    is_active: bool = True


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
