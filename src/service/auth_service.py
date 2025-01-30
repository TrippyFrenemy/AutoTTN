from fastapi import HTTPException, Request, Response

import secrets
from typing import Optional
import logging

from config import ADMIN_USERNAME, ADMIN_PASSWORD, SESSION_TOKEN_LENGTH

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# В реальном приложении это должно быть в базе данных
active_sessions = set()


def create_session_token() -> str:
    return secrets.token_urlsafe(int(SESSION_TOKEN_LENGTH))


def verify_credentials(username: str, password: str) -> bool:
    logger.debug(f"Attempting to verify credentials")
    logger.debug(f"Input username: '{username}', Input password: '{password}'")
    logger.debug(f"Expected username: '{ADMIN_USERNAME}', Expected password: '{ADMIN_PASSWORD}'")
    logger.debug(f"Username match: {username == ADMIN_USERNAME}")
    logger.debug(f"Password match: {password == ADMIN_PASSWORD}")

    # Явное сравнение строк
    is_username_valid = username.strip() == ADMIN_USERNAME.strip()
    is_password_valid = password.strip() == ADMIN_PASSWORD.strip()

    logger.debug(f"Username valid after strip: {is_username_valid}")
    logger.debug(f"Password valid after strip: {is_password_valid}")

    return is_username_valid and is_password_valid


def create_session(response: Response) -> str:
    session_token = create_session_token()
    logger.debug(f"Creating new session with token: {session_token[:8]}...")
    active_sessions.add(session_token)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,  # В продакшене с HTTPS установите True
        samesite='lax',
        max_age=3600  # 1 час
    )
    return session_token


def verify_session(request: Request) -> bool:
    session_token = request.cookies.get("session_token")
    logger.debug(f"Verifying session token: {session_token[:8] if session_token else None}...")
    is_valid = session_token in active_sessions
    logger.debug(f"Session valid: {is_valid}")
    return is_valid


def end_session(response: Response) -> None:
    response.delete_cookie(key="session_token")


def get_current_admin(request: Request) -> Optional[str]:
    if not verify_session(request):
        logger.debug("Session verification failed, redirecting to login")
        raise HTTPException(
            status_code=303,
            detail="Not authenticated",
            headers={"Location": "/auth/login"}
        )
    logger.debug("Session verified successfully")
    return ADMIN_USERNAME