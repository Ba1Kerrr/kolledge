from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy import func

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import get_current_user

router = APIRouter(prefix="/measurements", tags=["measurements"])

@router.get("/", response_model=List[schemas.Measurement])
def get_measurements(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Measurement).filter(models.Measurement.user_id == current_user.id)
    
    if start_date:
        query = query.filter(models.Measurement.date >= start_date)
    if end_date:
        query = query.filter(models.Measurement.date <= end_date)
    
    measurements = query.order_by(models.Measurement.date.desc()).offset(skip).limit(limit).all()
    return measurements

@router.get("/{measurement_id}", response_model=schemas.Measurement)
def get_measurement(
    measurement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id,
        models.Measurement.user_id == current_user.id
    ).first()
    
    if not measurement:
        raise HTTPException(status_code=404, detail="Измерение не найдено")
    
    return measurement

@router.post("/", response_model=schemas.Measurement, status_code=201)
def create_measurement(
    measurement_data: schemas.MeasurementCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_measurement = models.Measurement(user_id=current_user.id, **measurement_data.dict())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

@router.put("/{measurement_id}", response_model=schemas.Measurement)
def update_measurement(
    measurement_id: int,
    measurement_update: schemas.MeasurementBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id,
        models.Measurement.user_id == current_user.id
    ).first()
    
    if not measurement:
        raise HTTPException(status_code=404, detail="Измерение не найдено")
    
    for field, value in measurement_update.dict(exclude_unset=True).items():
        setattr(measurement, field, value)
    
    db.commit()
    db.refresh(measurement)
    return measurement

@router.delete("/{measurement_id}", status_code=204)
def delete_measurement(
    measurement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id,
        models.Measurement.user_id == current_user.id
    ).first()
    
    if not measurement:
        raise HTTPException(status_code=404, detail="Измерение не найдено")
    
    db.delete(measurement)
    db.commit()

@router.get("/stats/progress")
def get_progress_stats(
    period_days: int = Query(30, ge=7, le=365),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    weight_data = db.query(models.Measurement.date, models.Measurement.weight).filter(
        models.Measurement.user_id == current_user.id,
        models.Measurement.date >= start_date,
        models.Measurement.weight.isnot(None)
    ).order_by(models.Measurement.date).all()
    
    body_fat_data = db.query(models.Measurement.date, models.Measurement.body_fat).filter(
        models.Measurement.user_id == current_user.id,
        models.Measurement.date >= start_date,
        models.Measurement.body_fat.isnot(None)
    ).order_by(models.Measurement.date).all()
    
    return {
        "weight_data": [{"date": d, "weight": w} for d, w in weight_data],
        "body_fat_data": [{"date": d, "body_fat": bf} for d, bf in body_fat_data],
        "period": period_days
    }