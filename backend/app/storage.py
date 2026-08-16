"""Simple JSON-file storage for users and conversations.

This is a demo persist layer (not a database). You can swap it later
for MongoDB or similar without changing the API routes much.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
CONVERSATIONS_FILE = DATA_DIR / "conversations.json"

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for path in (USERS_FILE, CONVERSATIONS_FILE):
        if not path.exists():
            path.write_text("[]", encoding="utf-8")


def _read(path: Path) -> list:
    _ensure_files()
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


def _write(path: Path, data: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def get_user_by_username(username: str) -> Optional[dict]:
    needle = username.strip().lower()
    with _lock:
        for user in _read(USERS_FILE):
            if user.get("username", "").lower() == needle:
                return user
    return None


def get_user_by_id(user_id: str) -> Optional[dict]:
    with _lock:
        for user in _read(USERS_FILE):
            if user.get("id") == user_id:
                return user
    return None


def create_user(username: str, password_hash: str) -> Optional[dict]:
    """Create a user. Returns None if the username is already taken."""
    with _lock:
        users = _read(USERS_FILE)
        if any(user.get("username", "").lower() == username.lower() for user in users):
            return None
        user = {
            "id": str(uuid4()),
            "username": username,
            "password_hash": password_hash,
            "created_at": _now(),
        }
        users.append(user)
        _write(USERS_FILE, users)
        return user


def list_conversations(user_id: str) -> list:
    with _lock:
        conversations = [
            conv for conv in _read(CONVERSATIONS_FILE) if conv.get("user_id") == user_id
        ]
    conversations.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return [
        {
            "id": conv["id"],
            "title": conv.get("title") or "New chat",
            "created_at": conv.get("created_at"),
            "updated_at": conv.get("updated_at"),
        }
        for conv in conversations
    ]


def get_conversation(conversation_id: str) -> Optional[dict]:
    with _lock:
        for conv in _read(CONVERSATIONS_FILE):
            if conv.get("id") == conversation_id:
                return conv
    return None


def create_conversation(user_id: str, title: str = "New chat") -> dict:
    conversation = {
        "id": str(uuid4()),
        "user_id": user_id,
        "title": title,
        "created_at": _now(),
        "updated_at": _now(),
        "messages": [],
    }
    with _lock:
        conversations = _read(CONVERSATIONS_FILE)
        conversations.append(conversation)
        _write(CONVERSATIONS_FILE, conversations)
    return conversation


def append_messages(
    conversation_id: str,
    messages: list,
    title: Optional[str] = None,
) -> Optional[dict]:
    with _lock:
        conversations = _read(CONVERSATIONS_FILE)
        for conv in conversations:
            if conv.get("id") == conversation_id:
                conv.setdefault("messages", []).extend(messages)
                conv["updated_at"] = _now()
                if title:
                    conv["title"] = title
                _write(CONVERSATIONS_FILE, conversations)
                return conv
    return None


def delete_conversation(conversation_id: str, user_id: str) -> bool:
    with _lock:
        conversations = _read(CONVERSATIONS_FILE)
        kept = []
        deleted = False
        for conv in conversations:
            if conv.get("id") == conversation_id and conv.get("user_id") == user_id:
                deleted = True
                continue
            kept.append(conv)
        if deleted:
            _write(CONVERSATIONS_FILE, kept)
        return deleted
