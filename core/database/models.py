import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, BigInteger, Boolean, 
    DateTime, ForeignKey, Enum, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class MediaType(enum.Enum):
    VIDEO = "VIDEO"
    IMAGE = "IMAGE"

class ContentStatus(enum.Enum):
    DRAFT = "DRAFT"
    AI_GENERATED = "AI_GENERATED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(50), nullable=False, unique=True, index=True)
    drive_file_id = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    drive_url = Column(Text, nullable=False)
    file_type = Column(Enum(MediaType), nullable=False)
    extension = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    file_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Content(Base):
    __tablename__ = "contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(50), nullable=False, unique=True, index=True)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey("media_files.id"), nullable=True)
    raw_title = Column(Text, nullable=False)
    pillar_name = Column(String(100), nullable=True)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    content_score = Column(Numeric(3, 1), nullable=True)
    notes = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    media = relationship("MediaFile", backref="content_item", uselist=False)
