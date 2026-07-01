from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import close_mongo_connection, connect_to_mongo
from app.routers import auth, chat, history, metrics, model_tiering, prefix_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="AI Cost Optimizer POC",
    description="Demonstrates AI cost optimization using maximum token limits",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(metrics.router)
app.include_router(prefix_cache.router)
app.include_router(model_tiering.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
