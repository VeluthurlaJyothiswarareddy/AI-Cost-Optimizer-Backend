from datetime import datetime, timedelta, timezone
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.user import UserDocument

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthError("Invalid or expired token") from exc


class AuthService:
    async def register(self, collection, email: str, password: str) -> dict:
        normalized_email = email.lower()
        existing = await collection.find_one({"email": normalized_email})
        if existing:
            raise AuthError("Email is already registered")

        document = UserDocument.to_document(
            email=normalized_email,
            hashed_password=hash_password(password),
        )
        result = await collection.insert_one(document)
        user = UserDocument.serialize({**document, "_id": result.inserted_id})
        return {"user": user}

    async def login(self, collection, email: str, password: str) -> dict:
        normalized_email = email.lower()
        doc = await collection.find_one({"email": normalized_email})
        if not doc or not verify_password(password, doc["hashed_password"]):
            raise AuthError("Invalid email or password")

        user = UserDocument.serialize(doc)
        token = create_access_token(user["id"], user["email"])
        return {"access_token": token, "user": user}

    async def get_user_by_id(self, collection, user_id: str) -> dict | None:
        from bson import ObjectId
        from bson.errors import InvalidId

        try:
            doc = await collection.find_one({"_id": ObjectId(user_id)})
        except InvalidId:
            return None

        if not doc:
            return None
        return UserDocument.serialize(doc)

    async def is_token_revoked(self, revoked_collection, jti: str | None) -> bool:
        if not jti:
            return False
        doc = await revoked_collection.find_one({"jti": jti})
        return doc is not None

    async def revoke_token(self, revoked_collection, token: str) -> None:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        if not jti:
            return

        exp = payload.get("exp")
        expires_at = (
            datetime.fromtimestamp(exp, tz=timezone.utc)
            if exp
            else datetime.now(timezone.utc)
        )
        await revoked_collection.update_one(
            {"jti": jti},
            {"$set": {"jti": jti, "expires_at": expires_at}},
            upsert=True,
        )


auth_service = AuthService()
