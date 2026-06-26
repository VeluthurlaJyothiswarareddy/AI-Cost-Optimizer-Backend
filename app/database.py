from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, db
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.database_name]


async def close_mongo_connection() -> None:
    global client, db
    if client:
        client.close()
    client = None
    db = None


def get_database() -> AsyncIOMotorDatabase:
    if db is None:
        raise RuntimeError("Database is not initialized")
    return db


def get_collection():
    return get_database()["llm_requests"]


def get_prompt_cache_collection():
    return get_database()["prompt_cache"]


def get_model_tiering_collection():
    return get_database()["model_tiering"]


def get_model_routing_collection():
    return get_database()["model_routing_requests"]
