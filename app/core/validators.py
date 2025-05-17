"""DNS record validation utilities."""
import ipaddress
import re
from typing import Optional, Set

from sqlmodel import Session, select

from app.models import Host, Record, RecordType

# Constants
MAX_CNAME_CHAIN_LENGTH = 8
HOSTNAME_PATTERN = r'^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$'


def validate_hostname(hostname: str) -> bool:
    """Validate a hostname according to RFC 1123.
    
    Args:
        hostname: The hostname to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not hostname or len(hostname) > 253:
        return False
    return bool(re.fullmatch(HOSTNAME_PATTERN, hostname))


def validate_ipv4(ip: str) -> bool:
    """Validate an IPv4 address.
    
    Args:
        ip: The IP address to validate
        
    Returns:
        bool: True if valid IPv4, False otherwise
    """
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_record_value(record_type: RecordType, value: str) -> bool:
    """Validate a DNS record value based on its type.
    
    Args:
        record_type: Type of the DNS record
        value: The value to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not value:
        return False
        
    if record_type == RecordType.A:
        return validate_ipv4(value)
    elif record_type in (RecordType.CNAME, RecordType.MX):
        return validate_hostname(value)
    return True


def validate_no_conflicting_records(
    session: Session, 
    host_id: int, 
    record_type: RecordType,
    record_value: str,
    record_id: Optional[int] = None
) -> bool:
    """Check for conflicting records (e.g., CNAME with other records or duplicates).
    
    Args:
        session: Database session
        host_id: ID of the host
        record_type: Type of the record being added/updated
        record_value: Value of the record being added/updated
        record_id: ID of the record being updated (if any)
        
    Returns:
        bool: True if no conflicts, False otherwise
    """
    # Get all records for this host
    stmt = select(Record).where(Record.host_id == host_id)
    if record_id is not None:
        stmt = stmt.where(Record.id != record_id)
    
    existing_records = session.exec(stmt).all()
    
    # Check for duplicate record (same type and value)
    if any(r.type == record_type and r.value == record_value for r in existing_records):
        return False
    
    # Check for CNAME conflicts
    if record_type == RecordType.CNAME and existing_records:
        # Can't have CNAME with any other records
        return False
    
    # Check if adding a record when CNAME exists
    if any(r.type == RecordType.CNAME for r in existing_records):
        return False
        
    return True


def detect_cname_chain_loop(
    session: Session, 
    start_hostname: str, 
    visited: Optional[Set[str]] = None
) -> bool:
    """Detect if following CNAMEs creates a loop.
    
    Args:
        session: Database session
        start_hostname: Hostname to start checking from
        visited: Set of already visited hostnames (used for recursion)
        
    Returns:
        bool: True if a loop is detected, False otherwise
    """
    if visited is None:
        visited = set()
        
    if start_hostname in visited:
        return True
        
    if len(visited) >= MAX_CNAME_CHAIN_LENGTH:
        return True
        
    visited.add(start_hostname)
    
    # Get all CNAME records for this hostname
    host = session.exec(select(Host).where(Host.hostname == start_hostname)).first()
    if not host:
        return False
        
    cname_records = session.exec(
        select(Record)
        .where(Record.host_id == host.id)
        .where(Record.type == RecordType.CNAME)
    ).all()
    
    for record in cname_records:
        if detect_cname_chain_loop(session, record.value, visited.copy()):
            return True
            
    return False
