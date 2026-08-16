from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Ticket, CategoryEnum, PriorityEnum, StatusEnum
from app.schemas import (
    TicketCreate,
    TicketResponse,
    TicketDetailResponse,
    TicketUpdateStatus
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new IT support ticket. Default status is OPEN.
    """
    db_ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        category=ticket_in.category.value,
        priority=ticket_in.priority.value,
        status=StatusEnum.OPEN.value
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status_filter: Optional[StatusEnum] = Query(None, alias="status", description="Filter by ticket status"),
    priority_filter: Optional[PriorityEnum] = Query(None, alias="priority", description="Filter by priority level"),
    category_filter: Optional[CategoryEnum] = Query(None, alias="category", description="Filter by issue category"),
    db: Session = Depends(get_db)
):
    """
    List tickets with optional URL query filters for status, priority, and category.
    Ordered by creation date descending.
    """
    query = db.query(Ticket)

    if status_filter:
        query = query.filter(Ticket.status == status_filter.value)
    if priority_filter:
        query = query.filter(Ticket.priority == priority_filter.value)
    if category_filter:
        query = query.filter(Ticket.category == category_filter.value)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_detail(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch a detailed ticket record by ID, including nested comments and attachments.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: str,
    status_update: TicketUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Update ticket status (e.g. OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED).
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )

    ticket.status = status_update.status.value
    db.commit()
    db.refresh(ticket)
    return ticket
