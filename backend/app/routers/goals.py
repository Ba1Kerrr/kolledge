from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("/", response_model=List[schemas.Goal])
def get_goals(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goals = db.query(models.Goal).filter(
        models.Goal.user_id == current_user.id
    ).order_by(models.Goal.created_at.desc()).all()
    return goals

@router.get("/{goal_id}", response_model=schemas.Goal)
def get_goal(
    goal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    return goal

@router.post("/", response_model=schemas.Goal, status_code=201)
def create_goal(
    goal_data: schemas.GoalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_goal = models.Goal(user_id=current_user.id, **goal_data.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.put("/{goal_id}", response_model=schemas.Goal)
def update_goal(
    goal_id: int,
    goal_update: schemas.GoalBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    for field, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    db.delete(goal)
    db.commit()

@router.patch("/{goal_id}/complete", response_model=schemas.Goal)
def complete_goal(
    goal_id: int,
    current_value: float,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    goal.current_value = current_value
    goal.is_completed = True
    
    db.commit()
    db.refresh(goal)
    return goal