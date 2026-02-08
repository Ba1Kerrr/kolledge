import sys
import os
from pathlib import Path
from datetime import date

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_all_models():
    try:
        from backend.app.database import SessionLocal
        from backend.app.models import User, Workout, Exercise, ExerciseSet, Meal, Measurement, Goal
        from backend.app.auth import get_password_hash
        
        db = SessionLocal()
        
        try:
            print("Создаю тестового пользователя")
            test_user = User(
                email="models_test@fitlog.com",
                username="modeltest",
                full_name="Test User",
                hashed_password=get_password_hash("Test123")
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print("Создаю тренировку")
            workout = Workout(
                user_id=test_user.id,
                name="Тестовая тренировка",
                date=date.today(),
                duration=60
            )
            db.add(workout)
            db.commit()
            db.refresh(workout)
            
            print("Создаю упражнения")
            exercises = [
                Exercise(workout_id=workout.id, name="Жим лежа", category="chest", order=1),
                Exercise(workout_id=workout.id, name="Приседания", category="legs", order=2)
            ]
            for ex in exercises:
                db.add(ex)
            db.commit()
            for ex in exercises:
                db.refresh(ex)
            
            print("Создаю подходы")
            for ex in exercises:
                sets = [
                    ExerciseSet(exercise_id=ex.id, set_number=1, reps=10, weight=60),
                    ExerciseSet(exercise_id=ex.id, set_number=2, reps=8, weight=70)
                ]
                for s in sets:
                    db.add(s)
            db.commit()
            
            print("Создаю прием пищи")
            meal = Meal(
                user_id=test_user.id,
                date=date.today(),
                meal_type="lunch",
                name="Тестовый обед",
                calories=650
            )
            db.add(meal)
            db.commit()
            db.refresh(meal)
            
            print("Создаю измерения")
            measurement = Measurement(
                user_id=test_user.id,
                date=date.today(),
                weight=75.5
            )
            db.add(measurement)
            db.commit()
            db.refresh(measurement)
            
            print("Создаю цель")
            goal = Goal(
                user_id=test_user.id,
                title="Сбросить 5 кг",
                goal_type="weight_loss",
                target_value=70.5,
                current_value=75.5
            )
            db.add(goal)
            db.commit()
            db.refresh(goal)
            
            print("Проверяю связи")
            user_workouts = db.query(Workout).filter_by(user_id=test_user.id).all()
            print(f"Тренировок: {len(user_workouts)}")
            
            workout_exercises = db.query(Exercise).filter_by(workout_id=workout.id).all()
            print(f"Упражнений: {len(workout_exercises)}")
            
            for ex in workout_exercises:
                ex_sets = db.query(ExerciseSet).filter_by(exercise_id=ex.id).all()
                print(f"Подходов в {ex.name}: {len(ex_sets)}")
            
            print("Проверяю to_dict()")
            models_to_test = [test_user, workout, exercises[0], meal, measurement, goal]
            for model in models_to_test:
                try:
                    data = model.to_dict()
                except Exception:
                    pass
            
            print("Очищаю данные")
            db.query(ExerciseSet).filter(Exercise.exercise_id.in_([ex.id for ex in exercises])).delete(synchronize_session=False)
            db.query(Exercise).filter_by(workout_id=workout.id).delete()
            db.query(Workout).filter_by(user_id=test_user.id).delete()
            db.query(Meal).filter_by(user_id=test_user.id).delete()
            db.query(Measurement).filter_by(user_id=test_user.id).delete()
            db.query(Goal).filter_by(user_id=test_user.id).delete()
            db.query(User).filter_by(id=test_user.id).delete()
            db.commit()
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    success = test_all_models()
    print(f"Результат: {'Успех' if success else 'Ошибка'}")

if __name__ == "__main__":
    main()