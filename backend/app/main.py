# Capa PaaS: frontera HTTP hacia SaaS (Vercel) y telemetría desde edge (ai/).
# No importar módulos de ai/ ni servir el frontend desde aquí.
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGIN_REGEX, CORS_ORIGINS
from app.database import dispose_db, init_db, setup_tables
from app.routers import health, occupation


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await setup_tables()
    yield
    await dispose_db()


app = FastAPI(
    title="Monitoreo de Ocupación — API",
    description="Capa PaaS: mock, persistencia PostgreSQL e integración YOLO.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(occupation.router, prefix="/api/v1")
