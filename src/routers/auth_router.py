import logging
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.service.auth_service import verify_credentials, create_session, end_session, get_current_admin

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="src/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    logger.debug(f"Login attempt for username: {username}")

    if verify_credentials(username, password):
        logger.debug("Credentials verified successfully")
        response = RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)
        create_session(response)
        logger.debug("Session created, redirecting to admin panel")
        return response

    logger.debug("Invalid credentials, returning to login page")
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Неверный email или пароль",
            "username": username  # Сохраняем введенный email
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    end_session(response)
    return response
