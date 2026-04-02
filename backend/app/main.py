import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_pool, close_pool
from app.routers import stations, trips, reservations, health

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting up — opening connection pool")
    await init_pool()
    yield
    logger.info("Shutting down — closing connection pool")
    await close_pool()


app = FastAPI(
    title="Landline Shuttle Booking",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(stations.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(reservations.router, prefix="/api")
