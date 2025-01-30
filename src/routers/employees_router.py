from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.security import HTTPBasicCredentials
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from src.database import get_async_session
from src import models
from src.service.auth_service import get_current_admin

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def list_employees(
    request: Request,
    admin: HTTPBasicCredentials = Depends(get_current_admin),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(models.Employee))
    employees = result.scalars().all()

    month_ago = datetime.utcnow() - timedelta(days=30)
    stats = []

    for employee in employees:
        orders_result = await db.execute(
            select(models.Order)
            .where(
                models.Order.employee_id == employee.id,
                models.Order.created_at >= month_ago
            )
        )
        orders = orders_result.scalars().all()

        total_orders = len(orders)
        total_sales = sum(order.price for order in orders)
        total_commission = sum(order.employee_commission for order in orders if order.employee_commission)

        stats.append({
            'id': employee.id,
            'name': employee.name,
            'hourly_rate': employee.hourly_rate,
            'commission_percent': employee.commission_percent,
            'is_active': employee.is_active,
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_commission': total_commission
        })

    return templates.TemplateResponse(
        "employees.html",
        {
            "request": request,
            "employees": stats
        }
    )


@router.post("/add")
async def add_employee(
    request: Request,
    name: str = Form(...),
    hourly_rate: float = Form(...),
    commission_percent: float = Form(...),
    db: AsyncSession = Depends(get_async_session),
    admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    if hourly_rate < 0:
        raise HTTPException(status_code=400, detail="Hourly rate cannot be negative")
    if not 0 <= commission_percent <= 100:
        raise HTTPException(status_code=400, detail="Commission percent must be between 0 and 100")

    employee = models.Employee(
        name=name,
        hourly_rate=hourly_rate,
        commission_percent=commission_percent
    )

    db.add(employee)
    await db.commit()

    return RedirectResponse(url="/employees/", status_code=303)


@router.post("/{employee_id}/update")
async def update_employee(
    employee_id: int,
    name: str = Form(...),
    hourly_rate: float = Form(...),
    commission_percent: float = Form(...),
    db: AsyncSession = Depends(get_async_session),
    admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    if hourly_rate < 0:
        raise HTTPException(status_code=400, detail="Hourly rate cannot be negative")
    if not 0 <= commission_percent <= 100:
        raise HTTPException(status_code=400, detail="Commission percent must be between 0 and 100")

    await db.execute(
        update(models.Employee)
        .where(models.Employee.id == employee_id)
        .values(
            name=name,
            hourly_rate=hourly_rate,
            commission_percent=commission_percent
        )
    )
    await db.commit()

    return RedirectResponse(url="/employees/", status_code=303)


@router.get("/{employee_id}/stats")
async def get_employee_stats(
    employee_id: int,
    period_days: Optional[int] = 30,
    db: AsyncSession = Depends(get_async_session),
    admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    result = await db.execute(
        select(models.Employee).where(models.Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    period_start = datetime.utcnow() - timedelta(days=period_days)

    orders_result = await db.execute(
        select(models.Order)
        .where(
            models.Order.employee_id == employee_id,
            models.Order.created_at >= period_start
        )
    )
    orders = orders_result.scalars().all()

    stats = {
        'total_orders': len(orders),
        'total_sales': sum(order.price for order in orders),
        'total_commission': sum(order.employee_commission for order in orders if order.employee_commission),
        'orders_per_day': len(orders) / period_days if period_days > 0 else 0,
        'period_days': period_days
    }

    return stats


@router.post("/{employee_id}/toggle")
async def toggle_employee_status(
    employee_id: int,
    db: AsyncSession = Depends(get_async_session),
    admin: HTTPBasicCredentials = Depends(get_current_admin)
):
    result = await db.execute(
        select(models.Employee).where(models.Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.execute(
        update(models.Employee)
        .where(models.Employee.id == employee_id)
        .values(is_active=not employee.is_active)
    )
    await db.commit()

    return RedirectResponse(url="/employees/", status_code=303)
