"""Background tasks for the DNS API."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlmodel import Session, select

from app.core.database import get_session
from app.models import Record


class TaskScheduler:
    """Background task scheduler for periodic tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task[Any]] = {}
        self.running = False
    
    async def start(self) -> None:
        """Start all scheduled tasks."""
        if self.running:
            return
            
        self.running = True
        self.tasks["expire_records"] = asyncio.create_task(self._expire_records_worker())
        self.tasks["update_stats"] = asyncio.create_task(self._update_stats_worker())
    
    async def stop(self) -> None:
        """Stop all scheduled tasks."""
        self.running = False
        for task in self.tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def _expire_records_worker(self) -> None:
        """Background worker to clean up expired records."""
        while self.running:
            try:
                await self._expire_records()
            except Exception as e:
                print(f"Error in expire_records_worker: {e}")
            
            # Run every hour
            await asyncio.sleep(3600)
    
    async def _update_stats_worker(self) -> None:
        """Background worker to update statistics."""
        while self.running:
            try:
                await self._update_stats()
            except Exception as e:
                print(f"Error in update_stats_worker: {e}")
            
            # Run every 5 minutes
            await asyncio.sleep(300)
    
    async def _expire_records(self) -> None:
        """Expire records that are past their TTL."""
        with get_session() as session:
            # Get all records with TTL that have expired
            expired = session.exec(
                select(Record)
                .where(Record.updated_at < datetime.utcnow() - timedelta(seconds=Record.ttl))
            ).all()
            
            if expired:
                # In a real implementation, we might archive or delete expired records
                print(f"Found {len(expired)} expired records")
    
    async def _update_stats(self) -> None:
        """Update statistics about DNS records."""
        with get_session() as session:
            # Example: Count records by type
            record_types = session.exec(
                select(Record.type, func.count(Record.id))
                .group_by(Record.type)
            ).all()
            
            stats = {
                "record_counts": {r[0]: r[1] for r in record_types},
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # In a real implementation, we'd store these stats somewhere
            print(f"Updated stats: {stats}")


# Global task scheduler instance
task_scheduler = TaskScheduler()
