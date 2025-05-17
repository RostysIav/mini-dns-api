"""DNS API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core import tasks
from app.core.database import get_db_session
from app.core.resolver import resolve_hostname, ResolutionError
from app.core.validators import (
    validate_hostname,
    validate_record_value,
    validate_no_conflicting_records,
    detect_cname_chain_loop
)
from app.models import Host, HostCreate, HostRead, Record, RecordCreate, RecordRead, RecordType
from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    RecordValidationError,
    HostnameValidationError,
    CNAMELoopError,
    RecordConflictError
)

router = APIRouter(tags=["DNS"])

# Host endpoints
@router.post("/hosts/", response_model=HostRead, status_code=status.HTTP_201_CREATED)
async def create_host(host: HostCreate, session: Session = Depends(get_db_session)):
    """Create a new host.
    
    Args:
        host: Host data to create
        session: Database session
        
    Returns:
        Created host data
        
    Raises:
        HostnameValidationError: If hostname format is invalid
        ConflictError: If host already exists
        RecordValidationError: If there's an error creating the host
    """
    # Validate hostname
    if not validate_hostname(host.hostname):
        raise HostnameValidationError(
            detail=f"Invalid hostname format: {host.hostname}",
            error_code="INVALID_HOSTNAME"
        )
    
    # Check if host already exists
    existing = session.exec(select(Host).where(Host.hostname == host.hostname)).first()
    if existing:
        raise ConflictError(
            detail=f"Hostname '{host.hostname}' already exists",
            error_code="HOST_EXISTS"
        )
    
    # Create and save host
    db_host = Host.model_validate(host)
    session.add(db_host)
    
    try:
        session.commit()
        session.refresh(db_host)
        return db_host
    except Exception as e:
        session.rollback()
        raise RecordValidationError(
            detail=f"Error creating host: {str(e)}",
            error_code="HOST_CREATION_ERROR"
        )

@router.get("/hosts/", response_model=List[HostRead])
async def list_hosts(session: Session = Depends(get_db_session)):
    """List all hosts."""
    result = session.exec(select(Host)).all()
    return result

# Record endpoints
@router.post("/records/", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
async def create_record(record: RecordCreate, session: Session = Depends(get_db_session)):
    """Create a new DNS record.
    
    Args:
        record: Record data to create
        session: Database session
        
    Returns:
        Created record data
        
    Raises:
        NotFoundError: If host is not found
        RecordValidationError: If record validation fails
        RecordConflictError: If record conflicts with existing records
        CNAMELoopError: If CNAME record would create a loop
    """
    # Check if host exists
    host = session.get(Host, record.host_id)
    if not host:
        raise NotFoundError(
            detail=f"Host with ID {record.host_id} not found",
            error_code="HOST_NOT_FOUND"
        )
    
    # Validate record
    if not validate_record_value(record.type, record.value):
        raise RecordValidationError(
            detail=f"Invalid {record.type} record value: {record.value}",
            error_code="INVALID_RECORD_VALUE"
        )
    
    # Check for conflicts
    if not validate_no_conflicting_records(
        session=session,
        host_id=record.host_id,
        record_type=record.type,
        record_value=record.value
    ):
        raise RecordConflictError(
            detail=f"A record of type {record.type} with value {record.value} already exists for this host",
            error_code="RECORD_CONFLICT"
        )
    
    # Check for CNAME loops if this is a CNAME record
    if record.type == RecordType.CNAME:
        if detect_cname_chain_loop(session, record.value):
            raise CNAMELoopError(
                detail="CNAME record would create a loop",
                error_code="CNAME_LOOP_DETECTED"
            )
    
    # Create and save the record
    db_record = Record.model_validate(record)
    session.add(db_record)
    
    try:
        session.commit()
        session.refresh(db_record)
        return db_record
    except Exception as e:
        session.rollback()
        raise RecordValidationError(
            detail=f"Error creating record: {str(e)}",
            error_code="RECORD_CREATION_ERROR"
        )

@router.get("/records/", response_model=List[RecordRead])
async def list_records(session: Session = Depends(get_db_session)):
    """List all DNS records."""
    result = session.exec(select(Record)).all()
    return result

# DNS resolution endpoints
@router.get("/resolve/{hostname}")
async def resolve_hostname(
    hostname: str,
    type: Optional[RecordType] = None,
    follow_cname: bool = True,
    session: Session = Depends(get_db_session)
):
    """Resolve a hostname to its DNS records.
    
    Args:
        hostname: Hostname to resolve
        type: Optional record type to filter by
        follow_cname: Whether to follow CNAME records
        session: Database session
        
    Returns:
        Dict containing resolution results
        
    Raises:
        NotFoundError: If hostname cannot be resolved
        DNSError: If there's an error during resolution
    """
    try:
        return resolve_hostname(session, hostname, record_type=type)
    except ResolutionError as e:
        raise NotFoundError(
            detail=str(e),
            error_code="HOSTNAME_RESOLUTION_FAILED",
            extra={"hostname": hostname, "type": type.value if type else None}
        )
    except Exception as e:
        raise DNSError(
            detail=f"Error resolving hostname: {str(e)}",
            error_code="RESOLUTION_ERROR",
            extra={"hostname": hostname, "type": type.value if type else None}
        )


@router.get("/cname-chain/{hostname}")
async def get_cname_chain(
    hostname: str,
    max_depth: int = 10,
    session: Session = Depends(get_db_session)
):
    """Get the full CNAME chain for a hostname.
    
    Args:
        hostname: Starting hostname
        max_depth: Maximum depth to follow CNAMEs
        session: Database session
        
    Returns:
        Dict containing the CNAME chain and resolution status
        
    Raises:
        DNSError: If there's an error processing the CNAME chain
        CNAMELoopError: If a CNAME loop is detected
    """
    try:
        chain = []
        current = hostname
        visited = set()
        
        for _ in range(max_depth):
            if current in visited:
                raise CNAMELoopError(
                    detail=f"CNAME loop detected at {current}",
                    error_code="CNAME_LOOP_DETECTED",
                    extra={"hostname": hostname, "chain": chain}
                )
                
            visited.add(current)
            
            # Get all CNAME records for the current hostname
            stmt = select(Record).where(
                Record.host_id == Host.id,
                Host.hostname == current,
                Record.type == RecordType.CNAME
            )
            cname_records = session.exec(stmt).all()
            
            if not cname_records:
                return {
                    "hostname": hostname,
                    "chain": chain,
                    "resolved": True
                }
                
            if len(cname_records) > 1:
                raise DNSError(
                    detail=f"Multiple CNAME records found for {current}",
                    error_code="MULTIPLE_CNAMES",
                    extra={"hostname": current}
                )
                
            cname = cname_records[0]
            chain.append({
                "hostname": current,
                "cname": cname.value,
                "ttl": cname.ttl
            })
            current = cname.value
        
        return {
            "hostname": hostname,
            "chain": chain,
            "resolved": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
