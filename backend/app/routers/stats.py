from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta, datetime
from typing import Optional

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/dashboard")
def get_dashboard_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    total_workouts = db.query(func.count(models.Workout.id)).filter(
        models.Workout.user_id == current_user.id
    ).scalar() or 0
    
    weekly_workouts = db.query(func.count(models.Workout.id)).filter(
        models.Workout.user_id == current_user.id,
        models.Workout.date >= week_ago
    ).scalar() or 0
    
    week_nutrition = db.query(
        func.sum(models.Meal.calories).label('total_calories'),
        func.sum(models.Meal.protein).label('total_protein'),
        func.sum(models.Meal.carbs).label('total_carbs'),
        func.sum(models.Meal.fat).label('total_fat')
    ).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.date >= week_ago
    ).first()
    
    last_weight = db.query(models.Measurement.weight).filter(
        models.Measurement.user_id == current_user.id,
        models.Measurement.weight.isnot(None)
    ).order_by(models.Measurement.date.desc()).first()
    
    active_goals = db.query(func.count(models.Goal.id)).filter(
        models.Goal.user_id == current_user.id,
        models.Goal.is_completed == False
    ).scalar() or 0
    
    return {
        "workouts": {
            "total": total_workouts,
            "weekly": weekly_workouts,
            "avg_per_week": weekly_workouts
        },
        "nutrition": {
            "avg_daily_calories": (week_nutrition.total_calories or 0) / 7 if weekly_workouts > 0 else 0,
            "avg_protein": (week_nutrition.total_protein or 0) / 7 if weekly_workouts > 0 else 0,
            "avg_carbs": (week_nutrition.total_carbs or 0) / 7 if weekly_workouts > 0 else 0,
            "avg_fat": (week_nutrition.total_fat or 0) / 7 if weekly_workouts > 0 else 0
        },
        "measurements": {
            "last_weight": last_weight[0] if last_weight else None
        },
        "goals": {
            "active": active_goals
        }
    }

@router.get("/workouts/monthly")
def get_monthly_workout_stats(
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workouts_by_day = db.query(
        extract('day', models.Workout.date).label('day'),
        func.count(models.Workout.id).label('count'),
        func.sum(models.Workout.duration).label('total_duration')
    ).filter(
        models.Workout.user_id == current_user.id,
        extract('year', models.Workout.date) == year,
        extract('month', models.Workout.date) == month
    ).group_by('day').order_by('day').all()
    
    top_exercises = db.query(
        models.Exercise.name,
        func.count(models.Exercise.id).label('count')
    ).join(models.Workout).filter(
        models.Workout.user_id == current_user.id,
        extract('year', models.Workout.date) == year,
        extract('month', models.Workout.date) == month
    ).group_by(models.Exercise.name).order_by(func.count(models.Exercise.id).desc()).limit(5).all()
    
    return {
        "year": year,
        "month": month,
        "workouts_by_day": [
            {"day": int(day), "count": count, "total_duration": total_duration or 0}
            for day, count, total_duration in workouts_by_day
        ],
        "top_exercises": [
            {"name": name, "count": count}
            for name, count in top_exercises
        ]
    }

@router.get("/nutrition/daily")
def get_daily_nutrition_stats(
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
    
    total_calories = sum(m.calories or 0 for m in meals)
    total_protein = sum(m.protein or 0 for m in meals)
    total_carbs = sum(m.carbs or 0 for m in meals)
    total_fat = sum(m.fat or 0 for m in meals)
    
    meals_by_type = {}
    for meal in meals:
        if meal.meal_type not in meals_by_type:
            meals_by_type[meal.meal_type] = []
        meals_by_type[meal.meal_type].append({
            "name": meal.name,
            "calories": meal.calories,
            "protein": meal.protein,
            "carbs": meal.carbs,
            "fat": meal.fat
        })
    
    return {
        "date": target_date,
        "total": {
            "calories": total_calories,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat
        },
        "meals_by_type": meals_by_type
    }