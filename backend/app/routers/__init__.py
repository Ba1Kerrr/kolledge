from .users import router as users_router
from .workouts import router as workouts_router
from .meals import router as meals_router
from .measurements import router as measurements_router
from .goals import router as goals_router
from .stats import router as stats_router

__all__ = [
    "users_router",
    "workouts_router", 
    "meals_router",
    "measurements_router",
    "goals_router",
    "stats_router"
]