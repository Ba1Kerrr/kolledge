from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pathlib import Path
from sqlalchemy import text
from backend.app.database import SessionLocal

app = FastAPI(title="FitLog", docs_url=None, redoc_url=None)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.app.database import engine, Base
Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

FRONTEND_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

try:
    from backend.app.routers import users_router, workouts_router, meals_router
    from backend.app.routers import measurements_router, goals_router, stats_router
    
    app.include_router(users_router, prefix="/api")
    app.include_router(workouts_router, prefix="/api")
    app.include_router(meals_router, prefix="/api")
    app.include_router(measurements_router, prefix="/api")
    app.include_router(goals_router, prefix="/api")
    app.include_router(stats_router, prefix="/api")
    
except ImportError:
    @app.post("/api/users/register")
    async def demo_register():
        return {
            "success": True,
            "message": "Демо",
            "user": {"id": 1, "email": "demo@fitlog.com", "username": "demo"}
        }
    
    @app.post("/api/users/login")
    async def demo_login():
        return {
            "access_token": "demo-token",
            "token_type": "bearer",
            "user": {"id": 1, "email": "demo@fitlog.com", "username": "demo"}
        }

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>FitLog</h1>")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = FRONTEND_DIR / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/test")
async def test_api():
    return {"message": "API работает"}

@app.get("/api/debug/endpoints")
async def debug_endpoints():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name if hasattr(route, 'name') else None,
            "methods": list(route.methods) if hasattr(route, 'methods') else []
        })
    return {"total_endpoints": len(routes), "endpoints": routes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)