from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import date, timedelta

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import get_current_user

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("/", response_model=List[schemas.Workout])
def get_workouts(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Workout).filter(models.Workout.user_id == current_user.id)
    
    if start_date:
        query = query.filter(models.Workout.date >= start_date)
    if end_date:
        query = query.filter(models.Workout.date <= end_date)
    
    workouts = query.order_by(desc(models.Workout.date)).offset(skip).limit(limit).all()
    return workouts

@router.get("/{workout_id}", response_model=schemas.Workout)
def get_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    
    return workout

@router.post("/", response_model=schemas.Workout, status_code=201)
def create_workout(
    workout_data: schemas.WorkoutCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_workout = models.Workout(
        user_id=current_user.id,
        **workout_data.dict(exclude={"exercises"})
    )
    
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    for exercise_data in workout_data.exercises:
        db_exercise = models.Exercise(
            workout_id=db_workout.id,
            **exercise_data.dict(exclude={"sets"})
        )
        
        db.add(db_exercise)
        db.commit()
        db.refresh(db_exercise)
        
        for set_data in exercise_data.sets:
            db_set = models.ExerciseSet(exercise_id=db_exercise.id, **set_data.dict())
            db.add(db_set)
        
        db.commit()
    
    db.refresh(db_workout)
    return db_workout

@router.put("/{workout_id}", response_model=schemas.Workout)
def update_workout(
    workout_id: int,
    workout_update: schemas.WorkoutBase,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    
    for field, value in workout_update.dict(exclude_unset=True).items():
        setattr(workout, field, value)
    
    db.commit()
    db.refresh(workout)
    return workout

@router.delete("/{workout_id}", status_code=204)
def delete_workout(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    
    db.delete(workout)
    db.commit()

@router.get("/stats/summary")
def get_workout_summary(
    period: str = Query("month", pattern="^(week|month|year|all)$"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    
    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "month":
        start_date = today.replace(day=1)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
    else:
        start_date = None
    
    query = db.query(models.Workout).filter(models.Workout.user_id == current_user.id)
    
    if start_date:
        query = query.filter(models.Workout.date >= start_date)
    
    workouts = query.all()
    
    total_duration = sum(w.duration or 0 for w in workouts)
    total_workouts = len(workouts)
    
    exercises = (
        db.query(models.Exercise.name, func.count(models.Exercise.id).label('count'))
        .join(models.Workout)
        .filter(models.Workout.user_id == current_user.id)
        .group_by(models.Exercise.name)
        .order_by(func.count(models.Exercise.id).desc())
        .limit(5)
        .all()
    )
    
    return {
        "total_workouts": total_workouts,
        "total_duration_minutes": total_duration,
        "avg_duration": total_duration / total_workouts if total_workouts > 0 else 0,
        "favorite_exercises": [{"name": e[0], "count": e[1]} for e in exercises],
        "period": period
    }