"""API routes - Deals"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import Deal, Pipeline, Stage, Contact
from app.api.schemas import DealCreate, DealUpdate, DealResponse

router = APIRouter()


@router.get("/deals", response_model=List[DealResponse])
async def list_deals(
    pipeline_id: Optional[str] = None,
    stage_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all deals with optional filtering"""
    query = db.query(Deal)

    if pipeline_id:
        query = query.filter(Deal.pipeline_id == pipeline_id)

    if stage_id:
        query = query.filter(Deal.stage_id == stage_id)

    deals = query.offset(skip).limit(limit).all()
    return [DealResponse.from_orm(d) for d in deals]


@router.post("/deals", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal: DealCreate, db: Session = Depends(get_db)
):
    """Create a new deal"""
    # Validate pipeline exists
    pipeline = db.query(Pipeline).filter(Pipeline.id == deal.pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Validate stage is in pipeline
    stage = db.query(Stage).filter(Stage.id == deal.stage_id).first()
    if not stage or stage.pipeline_id != deal.pipeline_id:
        raise HTTPException(status_code=400, detail="Invalid stage for this pipeline")

    db_deal = Deal(
        title=deal.title,
        value=deal.value,
        stage_id=deal.stage_id,
        pipeline_id=deal.pipeline_id,
        contact_id=deal.contact_id,
        description=deal.description,
        probability=stage.probability if stage else 0,
    )

    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)

    return DealResponse.from_orm(db_deal)


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: str, db: Session = Depends(get_db)):
    """Get a specific deal by ID"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponse.from_orm(deal)


@router.put("/deals/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: str,
    deal_update: DealUpdate,
    db: Session = Depends(get_db),
):
    """Update a deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    update_data = deal_update.dict(exclude_unset=True)

    # If stage changed, update probability
    if "stage_id" in update_data and update_data["stage_id"] != deal.stage_id:
        new_stage = db.query(Stage).filter(Stage.id == update_data["stage_id"]).first()
        if new_stage:
            update_data["probability"] = new_stage.probability

    for field, value in update_data.items():
        setattr(deal, field, value)

    deal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(deal)

    return DealResponse.from_orm(deal)


@router.delete("/deals/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(deal_id: str, db: Session = Depends(get_db)):
    """Delete a deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    db.delete(deal)
    db.commit()

    return None


@router.post("/deals/{deal_id}/close")
async def close_deal(
    deal_id: str,
    is_won: bool,
    db: Session = Depends(get_db),
):
    """Close a deal as won or lost"""
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal.is_won = is_won
    deal.closed_at = datetime.utcnow()
    deal.stage_id = None  # No longer in pipeline

    db.commit()
    db.refresh(deal)

    return DealResponse.from_orm(deal)