from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, journeys, personas, ai, export, analytics, websocket

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist (dev convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Enterprise B2B Customer Journey Mapping API",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(journeys.router)
app.include_router(personas.router)
app.include_router(ai.router)
app.include_router(export.router)
app.include_router(analytics.router)
app.include_router(websocket.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}
