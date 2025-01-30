from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.database import get_async_session
from src.service.auth_service import get_current_admin

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


# Основные маршруты заказов
@router.get("/order-form", response_class=HTMLResponse)
async def order_form(
        request: Request,
        db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(models.Employee)
        .where(models.Employee.is_active)
        .order_by(models.Employee.name)
    )
    employees = result.scalars().all()

    return templates.TemplateResponse(
        "order_form.html",
        {
            "request": request,
            "employees": employees
        }
    )


# Маршрут для очереди упаковки - теперь доступен по /packing-queue
@router.get("/packing-queue", response_class=HTMLResponse)
async def packing_queue(
        request: Request,
        db: AsyncSession = Depends(get_async_session),
        admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    result = await db.execute(
        select(models.Order)
        .where(models.Order.is_paid)
        .order_by(models.Order.created_at.desc())
    )
    orders = result.scalars().all()

    return templates.TemplateResponse(
        "packing_queue.html",
        {"request": request, "orders": orders}
    )


@router.post("/orders/{order_id}/toggle-packed")
async def toggle_order_packed(
        order_id: int,
        db: AsyncSession = Depends(get_async_session),
        admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    result = await db.execute(
        select(models.Order).where(models.Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await db.execute(
        update(models.Order)
        .where(models.Order.id == order_id)
        .values(is_packed=not order.is_packed)
    )
    await db.commit()

    return {"success": True, "is_packed": not order.is_packed}


@router.post("/orders/{order_id}/toggle-payment")
async def toggle_order_payment(
        order_id: int,
        request: Request,
        db: AsyncSession = Depends(get_async_session),
        admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    result = await db.execute(
        select(models.Order).where(models.Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await db.execute(
        update(models.Order)
        .where(models.Order.id == order_id)
        .values(is_paid=not order.is_paid)
    )
    await db.commit()

    return {"success": True, "is_paid": not order.is_paid}


@router.get("/orders/list", response_class=HTMLResponse)
async def list_orders(
        request: Request,
        admin: HTTPBasicCredentials = Depends(get_current_admin),
        db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(models.Order)
        .order_by(models.Order.created_at.desc())
    )
    orders = result.scalars().all()
    return templates.TemplateResponse(
        "orders_list.html",
        {"request": request, "orders": orders}
    )
