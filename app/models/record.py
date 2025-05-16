"""DNS Record model."""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from pydantic import validator
from sqlalchemy import CheckConstraint, Column, DateTime, Enum as SQLEnum, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.host import Host


class RecordType(str, Enum):
    """DNS record types."""
    A = "A"
    CNAME = "CNAME"
    MX = "MX"


class RecordBase(SQLModel):
    """Base model for DNS Record."""
    type: RecordType = Field(
        sa_type=SQLEnum(RecordType),
        description="Type of DNS record (A, CNAME, MX)",
    )
    value: str = Field(
        max_length=1000,
        description="Value of the DNS record (IP for A, hostname for CNAME, mail server for MX)",
    )
    ttl: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Time to live in seconds (60-86400)",
    )
    priority: Optional[int] = Field(
        default=None,
        ge=0,
        le=65535,
        description="Priority for MX records (0-65535)",
    )
    host_id: int = Field(
        foreign_key="host.id",
        description="ID of the host this record belongs to",
    )

    @validator("value")
    def validate_value(cls, v: str, values: dict) -> str:
        """Validate the record value based on its type."""
        if "type" not in values:
            return v
            
        if values["type"] == RecordType.A:
            # Will be validated by the ARecord schema
            return v
        elif values["type"] == RecordType.CNAME:
            # Will be validated by the CNAMERecord schema
            return v.lower()
        elif values["type"] == RecordType.MX:
            # Will be validated by the MXRecord schema
            return v.lower()
        return v

    @validator("priority")
    def validate_priority(cls, v: Optional[int], values: dict) -> Optional[int]:
        """Validate priority is provided for MX records."""
        if "type" in values and values["type"] == RecordType.MX and v is None:
            raise ValueError("Priority is required for MX records")
        if "type" in values and values["type"] != RecordType.MX and v is not None:
            raise ValueError("Priority should only be set for MX records")
        return v


class Record(RecordBase, BaseModel, table=True):
    """Database model for DNS Record."""
    __table_args__ = (
        CheckConstraint(
            "(type != 'MX' AND priority IS NULL) OR (type = 'MX' AND priority IS NOT NULL)",
            name="check_mx_priority"
        ),
    )
    
    # Relationships
    host: "Host" = Relationship(back_populates="records")


class RecordCreate(RecordBase):
    """Schema for creating a new DNS Record."""
    pass


class RecordRead(RecordBase):
    """Schema for reading DNS Record data."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class RecordUpdate(SQLModel):
    """Schema for updating a DNS Record."""
    type: Optional[RecordType] = None
    value: Optional[str] = None
    ttl: Optional[int] = None
    priority: Optional[int] = None


class RecordList(SQLModel):
    """Schema for a list of DNS Records."""
    records: list[RecordRead]
    total: int


class ResolveResponse(SQLModel):
    """Schema for DNS resolution response."""
    hostname: str
    records: list[dict]
    resolved: bool
    canonical_name: Optional[str] = None
    error: Optional[str] = None
