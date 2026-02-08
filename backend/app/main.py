from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from backend.app.database import engine, Base
from backend.app.routers import users, workouts, meals, measurements, goals, stats

# Создаем таблицы
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск приложения
    print("FitLog API запущен!")
    yield
    # Завершение работы
    print("FitLog API остановлен")

app = FastAPI(
    title="FitLog API",
    description="API для журнала тренировок FitLog",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры
app.include_router(users.router, prefix="/api")
app.include_router(workouts.router, prefix="/api")
app.include_router(meals.router, prefix="/api")
app.include_router(measurements.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в FitLog API!",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "FitLog API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)