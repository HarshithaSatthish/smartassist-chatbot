import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.chatbot import process_message
from app.models import (
    AuthRequest,
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
    DeleteResponse,
    HealthResponse,
    TokenResponse,
    UserResponse,
)
from app import storage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


VERCEL_ORIGIN_REGEX = r"https://([a-z0-9-]+\.)*vercel\.app"


def get_cors_origins():
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://smartassist-chatbot.vercel.app",
    ]
    extra = os.getenv("CORS_ORIGINS", "")
    for item in extra.split(","):
        origin = item.strip().rstrip("/")
        if origin and origin not in origins:
            origins.append(origin)
    return origins


def _client_error_detail(exc: RequestValidationError, fallback: str) -> str:
    errors = exc.errors()
    if not errors:
        return fallback
    first = errors[0]
    msg = str(first.get("msg", "")).strip()
    if msg.startswith("Value error, "):
        return msg[len("Value error, ") :]
    loc = first.get("loc", ())
    field = loc[-1] if loc else ""
    if field == "message":
        return "Please enter a message."
    if field in {"username", "password"}:
        return "Please enter a username and password."
    return fallback


def _title_from_message(message: str, limit: int = 40) -> str:
    text = " ".join(message.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _token_response(user: dict) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user["id"], user["username"]),
        token_type="bearer",
        username=user["username"],
    )


def _owned_conversation(conversation_id: str, user: dict) -> dict:
    conversation = storage.get_conversation(conversation_id)
    if not conversation or conversation.get("user_id") != user["id"]:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


app = FastAPI(
    title="SmartAssist API",
    description="Backend for the SmartAssist AI chatbot.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=VERCEL_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def normalize_duplicate_slashes(request: Request, call_next):
    """Accept //path when VITE_API_URL was set with a trailing slash."""
    path = request.scope.get("path") or ""
    if "//" in path:
        request.scope["path"] = re.sub(r"/{2,}", "/", path)
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Turn invalid payloads into a clear error without stack traces."""
    path = request.url.path
    if path.startswith("/auth"):
        fallback = "Please enter a username and password."
    elif path == "/chat":
        fallback = "Please enter a message."
    else:
        fallback = "Invalid request."
    return JSONResponse(
        status_code=422,
        content={"detail": _client_error_detail(exc, fallback)},
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "service": "SmartAssist API"}


@app.post("/auth/register", response_model=TokenResponse)
async def register(request: AuthRequest):
    user = storage.create_user(request.username, hash_password(request.password))
    if user is None:
        raise HTTPException(status_code=409, detail="That username is already taken.")
    return _token_response(user)


@app.post("/auth/login", response_model=TokenResponse)
async def login(request: AuthRequest):
    user = storage.get_user_by_username(request.username)
    if not user or not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    return _token_response(user)


@app.get("/auth/me", response_model=UserResponse)
async def me(user: dict = Depends(get_current_user)):
    return UserResponse(username=user["username"])


@app.get("/conversations", response_model=list[ConversationSummary])
async def conversations(user: dict = Depends(get_current_user)):
    return storage.list_conversations(user["id"])


@app.post("/conversations", response_model=ConversationSummary)
async def new_conversation(user: dict = Depends(get_current_user)):
    conversation = storage.create_conversation(user["id"])
    return ConversationSummary(
        id=conversation["id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
    )


@app.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user),
):
    conversation = _owned_conversation(conversation_id, user)
    return ConversationDetail(
        id=conversation["id"],
        title=conversation.get("title") or "New chat",
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        messages=conversation.get("messages") or [],
    )


@app.delete("/conversations/{conversation_id}", response_model=DeleteResponse)
async def remove_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user),
):
    deleted = storage.delete_conversation(conversation_id, user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return DeleteResponse(ok=True)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    try:
        if request.conversation_id:
            conversation = _owned_conversation(request.conversation_id, user)
        else:
            conversation = storage.create_conversation(user["id"])

        reply, source = await process_message(request.message)
        now = datetime.now(timezone.utc).isoformat()
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": now,
        }
        bot_message = {
            "role": "bot",
            "content": reply,
            "timestamp": now,
        }

        title = None
        has_user_message = any(
            item.get("role") == "user" for item in conversation.get("messages") or []
        )
        if not has_user_message:
            title = _title_from_message(request.message)

        storage.append_messages(conversation["id"], [user_message, bot_message], title=title)
        return ChatResponse(
            reply=reply,
            source=source,
            conversation_id=conversation["id"],
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to process chat message.")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        )
