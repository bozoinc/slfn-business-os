"""Database models for SLFN Nexus Platform"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.session import Base


# Association table for contact tags
contact_tags = Table(
    "contact_tags",
    Base.metadata,
    Column("contact_id", String, ForeignKey("contacts.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
)


class Contact(Base):
    """Contact model for CRM"""

    __tablename__ = "contacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True, index=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    # Custom fields as JSON
    custom_fields = Column(JSON, default=dict)

    # Tags relationship
    tags = relationship("Tag", secondary=contact_tags, back_populates="contacts")

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Tag(Base):
    """Tag model for contact categorization"""

    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    color = Column(String, default="#3b82f6")  # Default Tailwind blue

    contacts = relationship("Contact", secondary=contact_tags, back_populates="tags")


class Pipeline(Base):
    """Sales pipeline model"""

    __tablename__ = "pipelines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    organization_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    stages = relationship("Stage", back_populates="pipeline", order_by="Stage.position")
    deals = relationship("Deal", back_populates="pipeline")


class Stage(Base):
    """Pipeline stage model"""

    __tablename__ = "stages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    position = Column(Integer)
    probability = Column(Integer, default=0)
    pipeline_id = Column(String, ForeignKey("pipelines.id"))

    pipeline = relationship("Pipeline", back_populates="stages")
    deals = relationship("Deal", back_populates="stage")


class Deal(Base):
    """Deal/Pipeline opportunity model"""

    __tablename__ = "deals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    value = Column(Integer, nullable=True)  # In cents
    stage_id = Column(String, ForeignKey("stages.id"))
    pipeline_id = Column(String, ForeignKey("pipelines.id"))
    contact_id = Column(String, ForeignKey("contacts.id"), nullable=True)

    description = Column(String, nullable=True)
    probability = Column(Integer, default=0)

    closed_at = Column(DateTime, nullable=True)
    is_won = Column(Boolean, default=None)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stage = relationship("Stage", back_populates="deals")
    pipeline = relationship("Pipeline", back_populates="deals")
    contact = relationship("Contact")


class Form(Base):
    """Lead capture form model"""

    __tablename__ = "forms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Form configuration
    fields = Column(JSON, default=list)  # Form field definitions
    settings = Column(JSON, default=dict)  # Form settings

    # Embed settings
    embed_code = Column(String, nullable=True)

    # Analytics
    submissions_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FormSubmission(Base):
    """Form submission model"""

    __tablename__ = "form_submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id = Column(String, ForeignKey("forms.id"))
    contact_id = Column(String, nullable=True)

    # Submission data
    data = Column(JSON)
    source = Column(String, nullable=True)  # website, mobile, etc.

    # IP and metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    form = relationship("Form")