from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.models import Ticket, StatusEnum, PriorityEnum
from app.schemas import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get aggregated ticket statistics grouped by status and priority.
    """
    total_tickets = db.query(func.count(Ticket.id)).scalar() or 0

    # Query counts grouped by status
    status_counts_raw = (
        db.query(Ticket.status, func.count(Ticket.id))
        .group_by(Ticket.status)
        .all()
    )
    # Initialize all status keys with 0
    by_status = {status_enum.value: 0 for status_enum in StatusEnum}
    for status_val, count in status_counts_raw:
        if status_val in by_status:
            by_status[status_val] = count
        else:
            by_status[status_val] = count

    # Query counts grouped by priority
    priority_counts_raw = (
        db.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )
    # Initialize all priority keys with 0
    by_priority = {priority_enum.value: 0 for priority_enum in PriorityEnum}
    for priority_val, count in priority_counts_raw:
        if priority_val in by_priority:
            by_priority[priority_val] = count
        else:
            by_priority[priority_val] = count

    return DashboardStatsResponse(
        total_tickets=total_tickets,
        by_status=by_status,
        by_priority=by_priority
    )
