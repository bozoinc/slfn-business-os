"""Pydantic schemas for API request/response models"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContactResponse(BaseModel):
    """Contact response schema"""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    """Contact creation schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ContactUpdate(BaseModel):
    """Contact update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DealResponse(BaseModel):
    """Deal response schema"""
    id: str
    title: str
    value: Optional[int] = None
    stage_id: Optional[str] = None
    pipeline_id: str
    contact_id: Optional[str] = None
    description: Optional[str] = None
    probability: int
    closed_at: Optional[datetime] = None
    is_won: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DealCreate(BaseModel):
    """Deal creation schema"""
    title: str
    value: Optional[int] = None
    stage_id: str
    pipeline_id: str
    contact_id: Optional[str] = None
    description: Optional[str] = None


class DealUpdate(BaseModel):
    """Deal update schema"""
    title: Optional[str] = None
    value: Optional[int] = None
    stage_id: Optional[str] = None
    contact_id: Optional[str] = None
    description: Optional[str] = None
    probability: Optional[int] = None


class FormField(BaseModel):
    """Form field definition"""
    id: str
    type: str  # text, email, number, select, etc.
    label: str
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None  # For select, radio, checkbox


class FormResponse(BaseModel):
    """Form response schema"""
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    fields: List[Dict[str, Any]]
    settings: Dict[str, Any]
    embed_code: Optional[str] = None
    submissions_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FormCreate(BaseModel):
    """Form creation schema"""
    name: str
    description: Optional[str] = None
    fields: List[Dict[str, Any]]
    settings: Optional[Dict[str, Any]] = None


class FormUpdate(BaseModel):
    """Form update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class FormSubmissionCreate(BaseModel):
    """Form submission schema (public endpoint)"""
    data: Dict[str, Any]
    source: Optional[str] = None


class FormSubmissionResponse(BaseModel):
    """Form submission response schema"""
    id: str
    form_id: str
    data: Dict[str, Any]
    source: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True