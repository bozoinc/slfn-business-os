"""API routes - Guidance Engine"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid

from app.db.session import get_db
from app.db.models import Phase, Checklist, ChecklistItem, Milestone, UserProgress, Contact
from app.api.schemas import (
    PhaseResponse, PhaseCreate, PhaseUpdate,
    ChecklistResponse, ChecklistCreate, ChecklistUpdate,
    ChecklistItemResponse, ChecklistItemCreate, ChecklistItemUpdate,
    MilestoneResponse, MilestoneCreate, MilestoneUpdate,
    UserProgressResponse, UserProgressCreate, UserProgressUpdate,
    PhaseWithDetailsResponse
)

router = APIRouter()


# =============================================================================
# PHASE ENDPOINTS
# =============================================================================

@router.get("/guidance/phases", response_model=List[PhaseResponse])
async def list_phases(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all business growth phases"""
    query = db.query(Phase)
    if active_only:
        query = query.filter(Phase.is_active == True)
    phases = query.order_by(Phase.order).offset(skip).limit(limit).all()
    return [PhaseResponse.from_orm(p) for p in phases]


@router.post("/guidance/phases", response_model=PhaseResponse, status_code=status.HTTP_201_CREATED)
async def create_phase(
    phase: PhaseCreate,
    db: Session = Depends(get_db),
):
    """Create a new business growth phase"""
    # Check for duplicate name
    existing = db.query(Phase).filter(Phase.name == phase.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phase with this name already exists"
        )
    # Check for duplicate order
    existing = db.query(Phase).filter(Phase.order == phase.order).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phase with this order already exists"
        )

    db_phase = Phase(
        name=phase.name,
        description=phase.description,
        order=phase.order,
    )

    db.add(db_phase)
    db.commit()
    db.refresh(db_phase)

    return PhaseResponse.from_orm(db_phase)


@router.get("/guidance/phases/{phase_id}", response_model=PhaseWithDetailsResponse)
async def get_phase(
    phase_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific phase with all checklists and milestones"""
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    # Get checklists with items
    checklists = db.query(Checklist).filter(Checklist.phase_id == phase_id).order_by(Checklist.order).all()
    checklist_responses = []
    for checklist in checklists:
        items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == checklist.id).order_by(ChecklistItem.order).all()
        checklist_response = ChecklistResponse.from_orm(checklist)
        checklist_response.items = [ChecklistItemResponse.from_orm(item) for item in items]
        checklist_responses.append(checklist_response)

    # Get milestones
    milestones = db.query(Milestone).filter(Milestone.phase_id == phase_id).order_by(Milestone.order).all()
    milestone_responses = [MilestoneResponse.from_orm(m) for m in milestones]

    phase_response = PhaseWithDetailsResponse.from_orm(phase)
    phase_response.checklists = checklist_responses
    phase_response.milestones = milestone_responses

    return phase_response


@router.put("/guidance/phases/{phase_id}", response_model=PhaseResponse)
async def update_phase(
    phase_id: str,
    phase_update: PhaseUpdate,
    db: Session = Depends(get_db),
):
    """Update a phase"""
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    update_data = phase_update.dict(exclude_unset=True)

    # Check for duplicate name
    if 'name' in update_data:
        existing = db.query(Phase).filter(Phase.name == update_data['name'], Phase.id != phase_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phase with this name already exists"
            )

    # Check for duplicate order
    if 'order' in update_data:
        existing = db.query(Phase).filter(Phase.order == update_data['order'], Phase.id != phase_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phase with this order already exists"
            )

    for field, value in update_data.items():
        setattr(phase, field, value)

    phase.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(phase)

    return PhaseResponse.from_orm(phase)


@router.delete("/guidance/phases/{phase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phase(
    phase_id: str,
    db: Session = Depends(get_db),
):
    """Delete a phase (cascades to checklists, items, milestones, user_progress)"""
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    db.delete(phase)
    db.commit()

    return None


# =============================================================================
# CHECKLIST ENDPOINTS
# =============================================================================

@router.get("/guidance/checklists", response_model=List[ChecklistResponse])
async def list_checklists(
    phase_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all checklists, optionally filtered by phase"""
    query = db.query(Checklist)
    if phase_id:
        query = query.filter(Checklist.phase_id == phase_id)
    if active_only:
        query = query.filter(Checklist.is_active == True)
    checklists = query.order_by(Checklist.order).all()

    responses = []
    for checklist in checklists:
        items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == checklist.id).order_by(ChecklistItem.order).all()
        checklist_response = ChecklistResponse.from_orm(checklist)
        checklist_response.items = [ChecklistItemResponse.from_orm(item) for item in items]
        responses.append(checklist_response)

    return responses


@router.post("/guidance/checklists", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    checklist: ChecklistCreate,
    db: Session = Depends(get_db),
):
    """Create a new checklist"""
    # Verify phase exists
    phase = db.query(Phase).filter(Phase.id == checklist.phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    db_checklist = Checklist(
        phase_id=checklist.phase_id,
        title=checklist.title,
        description=checklist.description,
        order=checklist.order,
        is_required=checklist.is_required,
    )

    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)

    response = ChecklistResponse.from_orm(db_checklist)
    response.items = []
    return response


@router.get("/guidance/checklists/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(
    checklist_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific checklist with items"""
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == checklist_id).order_by(ChecklistItem.order).all()
    response = ChecklistResponse.from_orm(checklist)
    response.items = [ChecklistItemResponse.from_orm(item) for item in items]

    return response


@router.put("/guidance/checklists/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    checklist_id: str,
    checklist_update: ChecklistUpdate,
    db: Session = Depends(get_db),
):
    """Update a checklist"""
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    update_data = checklist_update.dict(exclude_unset=True)

    # Verify phase exists if phase_id is being updated
    if 'phase_id' in update_data:
        phase = db.query(Phase).filter(Phase.id == update_data['phase_id']).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Phase not found")

    for field, value in update_data.items():
        setattr(checklist, field, value)

    checklist.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(checklist)

    items = db.query(ChecklistItem).filter(ChecklistItem.checklist_id == checklist_id).order_by(ChecklistItem.order).all()
    response = ChecklistResponse.from_orm(checklist)
    response.items = [ChecklistItemResponse.from_orm(item) for item in items]

    return response


@router.delete("/guidance/checklists/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: str,
    db: Session = Depends(get_db),
):
    """Delete a checklist (cascades to items and user_progress)"""
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    db.delete(checklist)
    db.commit()

    return None


# =============================================================================
# CHECKLIST ITEM ENDPOINTS
# =============================================================================

@router.post("/guidance/checklist-items", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist_item(
    item: ChecklistItemCreate,
    checklist_id: str = Query(..., description="Checklist ID"),
    db: Session = Depends(get_db),
):
    """Create a new checklist item"""
    # Verify checklist exists
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    db_item = ChecklistItem(
        checklist_id=checklist_id,
        title=item.title,
        description=item.description,
        order=item.order,
        is_required=item.is_required,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return ChecklistItemResponse.from_orm(db_item)


@router.put("/guidance/checklist-items/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    item_id: str,
    item_update: ChecklistItemUpdate,
    db: Session = Depends(get_db),
):
    """Update a checklist item"""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    update_data = item_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)

    return ChecklistItemResponse.from_orm(item)


@router.delete("/guidance/checklist-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    item_id: str,
    db: Session = Depends(get_db),
):
    """Delete a checklist item"""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    db.delete(item)
    db.commit()

    return None


# =============================================================================
# MILESTONE ENDPOINTS
# =============================================================================

@router.get("/guidance/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    phase_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all milestones, optionally filtered by phase"""
    query = db.query(Milestone)
    if phase_id:
        query = query.filter(Milestone.phase_id == phase_id)
    milestones = query.order_by(Milestone.order).all()
    return [MilestoneResponse.from_orm(m) for m in milestones]


@router.post("/guidance/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
):
    """Create a new milestone"""
    # Verify phase exists
    phase = db.query(Phase).filter(Phase.id == milestone.phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    db_milestone = Milestone(
        phase_id=milestone.phase_id,
        title=milestone.title,
        description=milestone.description,
        criteria=milestone.criteria or {},
        order=milestone.order,
    )

    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)

    return MilestoneResponse.from_orm(db_milestone)


@router.get("/guidance/milestones/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(
    milestone_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return MilestoneResponse.from_orm(milestone)


@router.put("/guidance/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: str,
    milestone_update: MilestoneUpdate,
    db: Session = Depends(get_db),
):
    """Update a milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    update_data = milestone_update.dict(exclude_unset=True)

    if 'phase_id' in update_data:
        phase = db.query(Phase).filter(Phase.id == update_data['phase_id']).first()
        if not phase:
            raise HTTPException(status_code=404, detail="Phase not found")

    for field, value in update_data.items():
        setattr(milestone, field, value)

    milestone.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(milestone)

    return MilestoneResponse.from_orm(milestone)


@router.delete("/guidance/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: str,
    db: Session = Depends(get_db),
):
    """Delete a milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    db.delete(milestone)
    db.commit()

    return None


# =============================================================================
# USER PROGRESS ENDPOINTS
# =============================================================================

@router.get("/guidance/progress", response_model=List[UserProgressResponse])
async def get_user_progress(
    user_id: str = Query(..., description="User ID (Contact ID)"),
    phase_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get user's progress across all or specific phase"""
    # Verify user exists
    user = db.query(Contact).filter(Contact.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(UserProgress).filter(UserProgress.user_id == user_id)
    if phase_id:
        query = query.filter(UserProgress.phase_id == phase_id)
    progress = query.order_by(UserProgress.created_at).all()
    return [UserProgressResponse.from_orm(p) for p in progress]


@router.post("/guidance/progress", response_model=UserProgressResponse, status_code=status.HTTP_201_CREATED)
async def record_user_progress(
    progress: UserProgressCreate,
    db: Session = Depends(get_db),
):
    """Record or update user progress on a checklist item"""
    # Verify user exists
    user = db.query(Contact).filter(Contact.id == progress.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify checklist item exists
    item = db.query(ChecklistItem).filter(ChecklistItem.id == progress.checklist_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    # Verify phase exists
    phase = db.query(Phase).filter(Phase.id == progress.phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    # Check if progress already exists (upsert)
    existing = db.query(UserProgress).filter(
        UserProgress.user_id == progress.user_id,
        UserProgress.checklist_item_id == progress.checklist_item_id
    ).first()

    if existing:
        # Update existing
        existing.is_completed = progress.is_completed
        existing.notes = progress.notes
        if progress.is_completed and not existing.completed_at:
            existing.completed_at = datetime.utcnow()
        elif not progress.is_completed:
            existing.completed_at = None
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return UserProgressResponse.from_orm(existing)
    else:
        # Create new
        db_progress = UserProgress(
            user_id=progress.user_id,
            checklist_item_id=progress.checklist_item_id,
            phase_id=progress.phase_id,
            is_completed=progress.is_completed,
            notes=progress.notes,
            completed_at=datetime.utcnow() if progress.is_completed else None,
        )
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return UserProgressResponse.from_orm(db_progress)


@router.put("/guidance/progress/{progress_id}", response_model=UserProgressResponse)
async def update_user_progress(
    progress_id: str,
    progress_update: UserProgressUpdate,
    db: Session = Depends(get_db),
):
    """Update user progress"""
    progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")

    update_data = progress_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(progress, field, value)

    if 'is_completed' in update_data:
        if update_data['is_completed'] and not progress.completed_at:
            progress.completed_at = datetime.utcnow()
        elif not update_data['is_completed']:
            progress.completed_at = None

    progress.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(progress)

    return UserProgressResponse.from_orm(progress)