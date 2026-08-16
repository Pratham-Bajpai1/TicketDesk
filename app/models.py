import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db import Base


class CategoryEnum(str, enum.Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    ACCESS = "Access"


class PriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class StatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=StatusEnum.OPEN.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan", order_by="Comment.created_at")
    attachments = relationship("Attachment", back_populates="ticket", cascade="all, delete-orphan", order_by="Attachment.created_at")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_key = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
