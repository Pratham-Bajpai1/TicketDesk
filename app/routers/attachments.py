import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Ticket, Attachment
from app.schemas import PresignRequest, PresignUrlRequest, PresignResponse, AttachmentResponse
from app.services.s3 import generate_presigned_upload_url

router = APIRouter(tags=["Attachments"])


@router.post("/api/attachments/presigned-url", response_model=PresignResponse, status_code=status.HTTP_201_CREATED)
def generate_presigned_url(
    request: PresignUrlRequest,
    db: Session = Depends(get_db)
):
    """
    Checklist compliance endpoint: Generate S3 Presigned URL using HTTP PUT method for target bucket ATTACHMENTS_BUCKET.
    Saves attachment metadata record in the database.
    """
    ticket = db.query(Ticket).filter(Ticket.id == request.ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{request.ticket_id}' not found."
        )

    unique_prefix = uuid.uuid4().hex[:8]
    sanitized_filename = request.filename.replace(" ", "_")
    file_key = f"attachments/{request.ticket_id}/{unique_prefix}_{sanitized_filename}"

    presigned_url = generate_presigned_upload_url(
        file_key=file_key,
        content_type=request.content_type
    )

    attachment = Attachment(
        ticket_id=ticket.id,
        file_name=request.filename,
        file_key=file_key,
        content_type=request.content_type
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return PresignResponse(
        presigned_url=presigned_url,
        file_key=file_key,
        attachment_id=attachment.id
    )


@router.post("/api/tickets/{ticket_id}/attachments/presign", response_model=PresignResponse, status_code=status.HTTP_201_CREATED)
def generate_attachment_presigned_url(
    ticket_id: str,
    request: PresignRequest,
    db: Session = Depends(get_db)
):
    """
    Generate S3 Pre-signed URL using HTTP PUT for direct browser uploads.
    """
    return generate_presigned_url(
        request=PresignUrlRequest(
            ticket_id=ticket_id,
            filename=request.filename,
            content_type=request.content_type
        ),
        db=db
    )


@router.get("/api/attachments/{ticket_id}", response_model=List[AttachmentResponse])
@router.get("/api/tickets/{ticket_id}/attachments", response_model=List[AttachmentResponse])
def list_attachments(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """
    List all file attachment metadata records associated with a ticket.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID '{ticket_id}' not found."
        )

    attachments = db.query(Attachment).filter(Attachment.ticket_id == ticket_id).order_by(Attachment.created_at.desc()).all()
    return attachments
