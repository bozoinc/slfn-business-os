"""API routes - Document Intake Pipeline"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid
import os
import json

from app.db.session import get_db
from app.db.models import Document, Contact, Phase, Checklist
from app.api.schemas import (
    DocumentResponse, DocumentCreate, DocumentUpdate, DocumentUploadResponse
)

router = APIRouter()

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9002")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "documents")


# =============================================================================
# DOCUMENT ENDPOINTS
# =============================================================================

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    phase_id: Optional[str] = None,
    checklist_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all documents with optional filtering"""
    query = db.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    if uploaded_by:
        query = query.filter(Document.uploaded_by == uploaded_by)
    if phase_id:
        query = query.filter(Document.phase_id == phase_id)
    if checklist_id:
        query = query.filter(Document.checklist_id == checklist_id)
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return [DocumentResponse.from_orm(d) for d in documents]


@router.post("/documents/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None),
    phase_id: Optional[str] = Form(None),
    checklist_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a PDF document for processing"""
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] or ".pdf"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Create document record
    db_document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        content_type=file.content_type,
        file_size=file_size,
        status="pending",
        uploaded_by=uploaded_by,
        phase_id=phase_id,
        checklist_id=checklist_id,
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # TODO: Save to MinIO and queue for processing
    # For now, just return the document ID
    return DocumentUploadResponse(
        document_id=db_document.id,
        filename=db_document.original_filename,
        status="pending",
        message="Document uploaded successfully. Processing will begin shortly."
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.from_orm(document)


@router.get("/documents/{document_id}/extracted", response_model=DocumentResponse)
async def get_document_extracted(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Get extracted content from a processed document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document processing not complete. Current status: {document.status}"
        )
    
    return DocumentResponse.from_orm(document)


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
):
    """Update a document (mainly for internal processing updates)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(document, field, value)
    
    if 'status' in update_data and update_data['status'] == 'completed':
        document.processed_at = datetime.utcnow()
    
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    return DocumentResponse.from_orm(document)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Also delete from MinIO
    
    db.delete(document)
    db.commit()
    
    return None


# =============================================================================
# PDF PROCESSING UTILITY (placeholder for background worker)
# =============================================================================

async def process_document(document_id: str, db: Session):
    """
    Process a document using pdf-inspector.
    This should be called by a background worker (e.g., Celery, RQ, or custom worker).
    """
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        
        # Update status to processing
        document.status = "processing"
        document.updated_at = datetime.utcnow()
        db.commit()
        
        # TODO: Get file from MinIO
        # For now, simulate processing
        await simulate_pdf_processing(document, db)
        
    except Exception as e:
        document.status = "failed"
        document.error_message = str(e)
        document.updated_at = datetime.utcnow()
        db.commit()


async def simulate_pdf_processing(document: Document, db: Session):
    """
    Simulate PDF processing. Replace with actual pdf-inspector integration.
    """
    # This is a placeholder - actual implementation would:
    # 1. Download from MinIO
    # 2. Run pdf-inspector to extract text and metadata
    # 3. Save extracted content
    # 4. Update document record
    
    document.extracted_text = f"Extracted text from {document.original_filename} (placeholder)"
    document.extracted_metadata = {
        "page_count": 1,
        "author": "Unknown",
        "creator": "pdf-inspector simulation",
        "producer": "SLFN Business OS Document Pipeline",
    }
    document.status = "completed"
    document.processed_at = datetime.utcnow()
    document.updated_at = datetime.utcnow()
    db.commit()


# For manual testing
@router.post("/documents/{document_id}/process", response_model=DocumentResponse)
async def trigger_document_processing(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Manually trigger document processing (for testing)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await process_document(document_id, db)
    db.refresh(document)
    return DocumentResponse.from_orm(document)