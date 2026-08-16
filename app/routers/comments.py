from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Ticket, Comment
from app.schemas import CommentCreate, CommentResponse

router = APIRouter(prefix="/api/tickets", tags=["Comments"])


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    ticket_id: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db)
):
    """
    Add a threaded comment to a specific ticket.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )

    db_comment = Comment(
        ticket_id=ticket.id,
        author=comment_in.author,
        comment_text=comment_in.comment_text
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def list_comments(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    Fetch all threaded comments for a ticket ordered chronologically by creation date.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )

    comments = db.query(Comment).filter(Comment.ticket_id == ticket_id).order_by(Comment.created_at.asc()).all()
    return comments
