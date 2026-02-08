from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date as date_type, datetime
from typing import Optional, List

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseSchema):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ExerciseSetBase(BaseSchema):
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    rest_time: Optional[int] = None
    completed: bool = True

class ExerciseSetCreate(ExerciseSetBase):
    pass

class ExerciseSet(ExerciseSetBase):
    id: int

class ExerciseBase(BaseSchema):
    name: str
    category: Optional[str] = None
    order: int = 0

class ExerciseCreate(ExerciseBase):
    sets: List[ExerciseSetCreate] = []

class Exercise(ExerciseBase):
    id: int
    sets: List[ExerciseSet] = []

class WorkoutBase(BaseSchema):
    date: date_type = Field(default_factory=date_type.today)
    name: str
    duration: Optional[int] = None
    notes: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    exercises: List[ExerciseCreate] = []

class Workout(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    exercises: List[Exercise] = []

class MealBase(BaseSchema):
    date: date_type = Field(default_factory=date_type.today)
    meal_type: str
    name: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    notes: Optional[str] = None
    time: Optional[datetime] = None

class MealCreate(MealBase):
    pass

class Meal(MealBase):
    id: int
    user_id: int

class MeasurementBase(BaseSchema):
    date: date_type = Field(default_factory=date_type.today)
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    neck: Optional[float] = None
    chest: Optional[float] = None
    waist: Optional[float] = None
    hips: Optional[float] = None
    biceps_left: Optional[float] = None
    biceps_right: Optional[float] = None
    thigh_left: Optional[float] = None
    thigh_right: Optional[float] = None
    calf_left: Optional[float] = None
    calf_right: Optional[float] = None

class MeasurementCreate(MeasurementBase):
    pass

class Measurement(MeasurementBase):
    id: int
    user_id: int

class GoalBase(BaseSchema):
    title: str
    description: Optional[str] = None
    goal_type: Optional[str] = None
    target_value: Optional[float] = None
    current_value: float = 0
    unit: str = "кг"
    deadline: Optional[date_type] = None
    is_completed: bool = False

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: int
    user_id: int
    created_at: datetime

class WorkoutStats(BaseSchema):
    total_workouts: int
    total_duration: int
    avg_duration: float
    workouts_by_month: dict
    favorite_exercises: List[dict]

class NutritionStats(BaseSchema):
    total_calories: float
    avg_calories_per_day: float
    avg_protein: float
    avg_carbs: float
    avg_fat: float
    calories_by_day: List[dict]

class ProgressStats(BaseSchema):
    weight_data: List[dict]
    body_fat_data: List[dict]
    measurements_data: dict
    first_record: date_type
    last_record: date_type