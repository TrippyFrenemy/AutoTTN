from datetime import datetime, timedelta

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src import models
from src.database import get_async_session
from src.service.auth_service import verify_credentials, create_session, end_session, get_current_admin

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_current_admin)],
    responses={401: {"description": "Not authenticated"}}
)
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def admin_panel(
        request: Request,
        db: AsyncSession = Depends(get_async_session)
):
    # Get statistics
    total_orders = await db.scalar(select(func.count()).select_from(models.Order))

    total_revenue_result = await db.scalar(
        select(func.sum(models.Order.price)).select_from(models.Order)
    )
    total_revenue = total_revenue_result or 0

    paid_orders = await db.scalar(
        select(func.count())
        .select_from(models.Order)
        .where(models.Order.is_paid)
    )

    # Get recent orders with employee information
    recent_orders_result = await db.execute(
        select(models.Order)
        .options(joinedload(models.Order.employee))
        .order_by(models.Order.created_at.desc())
        .limit(10)
    )
    recent_orders = recent_orders_result.scalars().all()

    # Calculate employee statistics
    month_ago = datetime.utcnow() - timedelta(days=30)
    employee_stats = []

    employees_result = await db.execute(select(models.Employee))
    employees = employees_result.scalars().all()

    for employee in employees:
        orders_result = await db.execute(
            select(models.Order)
            .where(
                models.Order.employee_id == employee.id,
                models.Order.created_at >= month_ago
            )
        )
        employee_orders = orders_result.scalars().all()

        total_sales = sum(order.price for order in employee_orders)
        total_commission = sum(order.employee_commission for order in employee_orders if order.employee_commission)

        employee_stats.append({
            'name': employee.name,
            'total_orders': len(employee_orders),
            'total_sales': total_sales,
            'total_commission': total_commission,
            'hourly_rate': employee.hourly_rate,
            'is_active': employee.is_active
        })

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "paid_orders": paid_orders,
            "recent_orders": recent_orders,
            "employee_stats": employee_stats
        }
    )


@router.get("/orders/", response_class=HTMLResponse)
async def list_orders(
        request: Request,
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
