"""Host model for DNS records."""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.record import Record

class HostBase(SQLModel):
    """Base model for Host."""
    hostname: str = Field(
        index=True,
        nullable=False,
        description="Fully qualified domain name (e.g., example.com)",
        max_length=253,
    )
    description: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Optional description of the host",
        max_length=255,
    )

class Host(HostBase, BaseModel, table=True):
    """Database model for DNS Host."""
    __table_args__ = (
        UniqueConstraint("hostname", name="uq_host_hostname"),
    )
    
    # Relationships
    records: List["Record"] = Relationship(back_populates="host")

class HostCreate(HostBase):
    """Schema for creating a new Host."""
    pass

class HostRead(HostBase):
    """Schema for reading Host data."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class HostUpdate(SQLModel):
    """Schema for updating a Host."""
    hostname: Optional[str] = Field(
        default=None,
        max_length=253,
        description="New hostname"
    )
