from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models import CategoryEnum, PriorityEnum, StatusEnum


# --- Health Schema ---
class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    database: str = Field(..., example="connected")


# --- Attachment Schemas ---
class PresignRequest(BaseModel):
    filename: str = Field(..., example="screenshot.png", min_length=1)
    content_type: str = Field(default="application/octet-stream", example="image/png")


class PresignUrlRequest(BaseModel):
    ticket_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    filename: str = Field(..., example="screenshot.png", min_length=1)
    content_type: str = Field(default="application/octet-stream", example="image/png")


class PresignResponse(BaseModel):
    presigned_url: str
    file_key: str
    attachment_id: str


class AttachmentResponse(BaseModel):
    id: str
    ticket_id: str
    file_name: str
    file_key: str
    content_type: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Comment Schemas ---
class CommentCreate(BaseModel):
    author: str = Field(..., example="John Doe", min_length=1)
    comment_text: str = Field(..., example="Investigating network switch logs.", min_length=1)


class CommentResponse(BaseModel):
    id: str
    ticket_id: str
    author: str
    comment_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Ticket Schemas ---
class TicketCreate(BaseModel):
    title: str = Field(..., example="VPN Connection Failed", min_length=3, max_length=255)
    description: str = Field(..., example="Unable to authenticate with corporate VPN server after password reset.", min_length=5)
    category: CategoryEnum = Field(..., example=CategoryEnum.NETWORK)
    priority: PriorityEnum = Field(..., example=PriorityEnum.HIGH)


class TicketUpdateStatus(BaseModel):
    status: StatusEnum = Field(..., example=StatusEnum.IN_PROGRESS)


class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    category: CategoryEnum
    priority: PriorityEnum
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(TicketResponse):
    comments: List[CommentResponse] = []
    attachments: List[AttachmentResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Stats Schema ---
class DashboardStatsResponse(BaseModel):
    total_tickets: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
