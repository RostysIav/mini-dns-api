"""Base SQLModel for all database models."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """Base model with common fields."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": "CURRENT_TIMESTAMP"}
    )

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
