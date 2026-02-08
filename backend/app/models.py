from sqlalchemy import Column, Integer, String, Float, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workouts = relationship("Workout", back_populates="owner", cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="owner", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="owner", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="owner", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=datetime.utcnow().date(), nullable=False)
    name = Column(String(100), nullable=False)
    duration = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="workouts")
    exercises = relationship("Exercise", back_populates="workout", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'name': self.name,
            'duration': self.duration,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'exercises': [ex.to_dict() for ex in self.exercises] if self.exercises else []
        }

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    order = Column(Integer, default=0)
    
    workout = relationship("Workout", back_populates="exercises")
    sets = relationship("ExerciseSet", back_populates="exercise", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'workout_id': self.workout_id,
            'name': self.name,
            'category': self.category,
            'order': self.order,
            'sets': [s.to_dict() for s in self.sets] if self.sets else []
        }

class ExerciseSet(Base):
    __tablename__ = "exercise_sets"
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer)
    weight = Column(Float)
    rest_time = Column(Integer)
    completed = Column(Boolean, default=True)
    
    exercise = relationship("Exercise", back_populates="sets")
    
    def to_dict(self):
        return {
            'id': self.id,
            'exercise_id': self.exercise_id,
            'set_number': self.set_number,
            'reps': self.reps,
            'weight': self.weight,
            'rest_time': self.rest_time,
            'completed': self.completed
        }

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=datetime.utcnow().date(), nullable=False)
    meal_type = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    notes = Column(Text)
    time = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="meals")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'meal_type': self.meal_type,
            'name': self.name,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'notes': self.notes,
            'time': self.time.isoformat() if self.time else None
        }

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=datetime.utcnow().date(), nullable=False)
    weight = Column(Float)
    body_fat = Column(Float)
    neck = Column(Float)
    chest = Column(Float)
    waist = Column(Float)
    hips = Column(Float)
    biceps_left = Column(Float)
    biceps_right = Column(Float)
    thigh_left = Column(Float)
    thigh_right = Column(Float)
    calf_left = Column(Float)
    calf_right = Column(Float)
    
    owner = relationship("User", back_populates="measurements")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'weight': self.weight,
            'body_fat': self.body_fat,
            'neck': self.neck,
            'chest': self.chest,
            'waist': self.waist,
            'hips': self.hips,
            'biceps_left': self.biceps_left,
            'biceps_right': self.biceps_right,
            'thigh_left': self.thigh_left,
            'thigh_right': self.thigh_right,
            'calf_left': self.calf_left,
            'calf_right': self.calf_right
        }

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_type = Column(String(50))
    target_value = Column(Float)
    current_value = Column(Float, default=0)
    unit = Column(String(20), default="кг")
    deadline = Column(Date)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="goals")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }