from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import init_db
from app.routes import auth as auth_routes
from app.routes import entities as entities_routes
from app.routes import search as search_routes
from app.routes import share as share_routes
from app.routes import sync as sync_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="OrbisX API",
    description="Plug-and-play medie-intelligence-motor",
    version="0.0.1",
    lifespan=lifespan,
)

app.include_router(auth_routes.router)
app.include_router(entities_routes.router)
app.include_router(sync_routes.router)
app.include_router(search_routes.router)
app.include_router(share_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "OrbisX API",
        "version": "0.0.1",
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
