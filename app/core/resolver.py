"""DNS resolution utilities."""
from typing import Dict, List, Optional, Set, Tuple

from sqlmodel import Session, select

from app.core.validators import MAX_CNAME_CHAIN_LENGTH, detect_cname_chain_loop
from app.models import Host, Record, RecordType


class ResolutionError(Exception):
    """Exception raised for DNS resolution errors."""
    pass


def resolve_hostname_chain(
    session: Session,
    hostname: str,
    follow_cname: bool = True,
    max_depth: int = MAX_CNAME_CHAIN_LENGTH,
    _depth: int = 0,
    _visited: Optional[Set[str]] = None
) -> Tuple[str, List[Dict]]:
    """Resolve a hostname to its final destination following CNAME chains.
    
    Args:
        session: Database session
        hostname: Hostname to resolve
        follow_cname: Whether to follow CNAME records
        max_depth: Maximum depth for CNAME chain resolution
        _depth: Current recursion depth (internal use)
        _visited: Set of visited hostnames (internal use)
        
    Returns:
        Tuple of (canonical_name, list_of_records)
        
    Raises:
        ResolutionError: If resolution fails or a loop is detected
    """
    if _visited is None:
        _visited = set()
    
    if _depth > max_depth:
        raise ResolutionError(f"Maximum CNAME chain length ({max_depth}) exceeded")
    
    if hostname in _visited:
        raise ResolutionError(f"CNAME loop detected at {hostname}")
    
    _visited.add(hostname)
    
    # Find the host
    host = session.exec(select(Host).where(Host.hostname == hostname)).first()
    if not host:
        raise ResolutionError(f"Hostname '{hostname}' not found")
    
    # Get all records for this host
    records = session.exec(select(Record).where(Record.host_id == host.id)).all()
    
    # If following CNAMEs, check for CNAME records
    if follow_cname:
        cname_records = [r for r in records if r.type == RecordType.CNAME]
        if cname_records:
            if len(cname_records) > 1:
                raise ResolutionError("Multiple CNAME records found")
            
            cname = cname_records[0].value
            try:
                return resolve_hostname_chain(
                    session, cname, True, max_depth, _depth + 1, _visited
                )
            except ResolutionError as e:
                raise ResolutionError(f"Error resolving CNAME {hostname} -> {cname}: {str(e)}")
    
    # Return the records for this host
    return hostname, [
        {"type": r.type, "value": r.value, "ttl": r.ttl, "priority": r.priority}
        for r in records
    ]


def resolve_hostname(
    session: Session, hostname: str, record_type: Optional[RecordType] = None
) -> Dict:
    """Resolve a hostname to its DNS records.
    
    Args:
        session: Database session
        hostname: Hostname to resolve
        record_type: Optional record type to filter by
        
    Returns:
        Dict containing resolution results
    """
    try:
        # First try to resolve the hostname
        canonical_name, all_records = resolve_hostname_chain(session, hostname)
        
        # Filter by record type if specified
        if record_type:
            records = [r for r in all_records if r["type"] == record_type]
        else:
            records = all_records
        
        return {
            "hostname": hostname,
            "canonical_name": canonical_name,
            "records": records,
            "resolved": bool(records),
            "error": None
        }
        
    except ResolutionError as e:
        return {
            "hostname": hostname,
            "records": [],
            "resolved": False,
            "error": str(e)
        }
