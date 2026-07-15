"""API routes - Forms"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import Form, FormSubmission
from app.api.schemas import FormCreate, FormUpdate, FormResponse, FormSubmissionCreate

router = APIRouter()


@router.get("/forms", response_model=List[FormResponse])
async def list_forms(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all forms"""
    forms = db.query(Form).offset(skip).limit(limit).all()
    return [FormResponse.from_orm(f) for f in forms]


@router.post("/forms", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    form: FormCreate, db: Session = Depends(get_db)
):
    """Create a new form"""
    db_form = Form(
        name=form.name,
        description=form.description,
        fields=form.fields,
        settings=form.settings or {},
    )

    db.add(db_form)
    db.commit()
    db.refresh(db_form)

    # Generate embed code
    db_form.embed_code = f'<script src="https://localhost:3000/embed/{db_form.id}.js"></script>'
    db.commit()
    db.refresh(db_form)

    return FormResponse.from_orm(db_form)


@router.get("/forms/{form_id}", response_model=FormResponse)
async def get_form(form_id: str, db: Session = Depends(get_db)):
    """Get a specific form by ID"""
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return FormResponse.from_orm(form)


@router.put("/forms/{form_id}", response_model=FormResponse)
async def update_form(
    form_id: str,
    form_update: FormUpdate,
    db: Session = Depends(get_db),
):
    """Update a form"""
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    update_data = form_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(form, field, value)

    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(form)

    return FormResponse.from_orm(form)


@router.delete("/forms/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form(form_id: str, db: Session = Depends(get_db)):
    """Delete a form"""
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    db.delete(form)
    db.commit()

    return None


@router.post("/forms/{form_id}/submit")
async def submit_form(
    form_id: str,
    submission: FormSubmissionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Submit a form (public endpoint)"""
    form = db.query(Form).filter(Form.id == form_id, Form.is_active == True).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or inactive")

    # Create submission
    db_submission = FormSubmission(
        form_id=form_id,
        data=submission.data,
        source=submission.source,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", ""),
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    # Update form submission count
    form.submissions_count += 1
    db.commit()

    return {"success": True, "submission_id": db_submission.id}