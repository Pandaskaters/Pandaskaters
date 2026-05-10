from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import init_db
from app.routers import auth, rides, drivers, admin, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _create_admin_if_missing()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


async def _create_admin_if_missing():
    from app.database import AsyncSessionLocal
    from app.models.user import User, UserRole
    from app.utils.password_handler import hash_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.role == UserRole.admin))
        if not result.scalar_one_or_none():
            admin_user = User(
                name="Admin",
                email="admin@pandaskaters.com",
                phone="0000000000",
                hashed_password=hash_password("admin123"),
                role=UserRole.admin,
                is_active=True,
                is_verified=True,
            )
            db.add(admin_user)
            await db.commit()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(rides.router, prefix="/api")
app.include_router(drivers.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(websocket.router)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
