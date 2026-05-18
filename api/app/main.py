from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="OrbisX API",
    description="Plug-and-play medie-intelligence-motor",
    version="0.0.1",
    lifespan=lifespan,
)

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
