"""DNS API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_db_session
from app.models import Host, HostCreate, HostRead, Record, RecordCreate, RecordRead, RecordType

router = APIRouter(tags=["DNS"])

# Host endpoints
@router.post("/hosts/", response_model=HostRead, status_code=status.HTTP_201_CREATED)
async def create_host(host: HostCreate, session: Session = Depends(get_db_session)):
    """Create a new host."""
    db_host = Host.model_validate(host)
    session.add(db_host)
    try:
        session.commit()
        session.refresh(db_host)
        return db_host
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating host: {str(e)}"
        )

@router.get("/hosts/", response_model=List[HostRead])
async def list_hosts(session: Session = Depends(get_db_session)):
    """List all hosts."""
    result = session.exec(select(Host)).all()
    return result

# Record endpoints
@router.post("/records/", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
async def create_record(record: RecordCreate, session: Session = Depends(get_db_session)):
    """Create a new DNS record."""
    # Check if host exists
    host = session.get(Host, record.host_id)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host with ID {record.host_id} not found"
        )
    
    # Create the record
    db_record = Record.model_validate(record)
    session.add(db_record)
    
    try:
        session.commit()
        session.refresh(db_record)
        return db_record
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating record: {str(e)}"
        )

@router.get("/records/", response_model=List[RecordRead])
async def list_records(session: Session = Depends(get_db_session)):
    """List all DNS records."""
    result = session.exec(select(Record)).all()
    return result

# DNS resolution endpoint
@router.get("/resolve/{hostname}")
async def resolve_hostname(hostname: str, session: Session = Depends(get_db_session)):
    """Resolve a hostname to its DNS records."""
    # This is a simplified version - will be enhanced with CNAME resolution
    host = session.exec(select(Host).where(Host.hostname == hostname)).first()
    if not host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hostname '{hostname}' not found"
        )
    
    records = session.exec(select(Record).where(Record.host_id == host.id)).all()
    
    return {
        "hostname": host.hostname,
        "records": [{"type": r.type, "value": r.value, "ttl": r.ttl} for r in records]
    }
