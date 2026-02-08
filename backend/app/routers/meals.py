from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import get_current_user

router = APIRouter(prefix="/meals", tags=["meals"])

@router.get("/", response_model=List[schemas.Meal])
def get_meals(
    skip: int = 0,
    limit: int = 100,
    date_filter: Optional[date] = None,
    meal_type: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Meal).filter(models.Meal.user_id == current_user.id)
    
    if date_filter:
        query = query.filter(models.Meal.date == date_filter)
    if meal_type:
        query = query.filter(models.Meal.meal_type == meal_type)
    
    meals = query.order_by(models.Meal.date.desc()).offset(skip).limit(limit).all()
    return meals

@router.get("/{meal_id}", response_model=schemas.Meal)
def get_meal(
    meal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Прием пищи не найден")
    
    return meal

@router.post("/", response_model=schemas.Meal, status_code=201)
def create_meal(
    meal_data: schemas.MealCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_meal = models.Meal(user_id=current_user.id, **meal_data.dict())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@router.put("/{meal_id}", response_model=schemas.Meal)
def update_meal(
    meal_id: int,
    meal_update: schemas.MealBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Прием пищи не найден")
    
    for field, value in meal_update.dict(exclude_unset=True).items():
        setattr(meal, field, value)
    
    db.commit()
    db.refresh(meal)
    return meal

@router.delete("/{meal_id}", status_code=204)
def delete_meal(
    meal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Прием пищи не найден")
    
    db.delete(meal)
    db.commit()

@router.get("/daily/summary")
def get_daily_summary(
    target_date: Optional[date] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not target_date:
        target_date = date.today()
    
    meals = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.date == target_date
    ).all()
    
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    
    for meal in meals:
        totals["calories"] += meal.calories or 0
        totals["protein"] += meal.protein or 0
        totals["carbs"] += meal.carbs or 0
        totals["fat"] += meal.fat or 0
    
    return {
        "date": target_date,
        "meal_count": len(meals),
        "totals": totals,
        "meals": [{"name": m.name, "type": m.meal_type} for m in meals]
    }