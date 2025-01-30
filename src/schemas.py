from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EmployeeBase(BaseModel):
    name: str
    hourly_rate: float = Field(..., gt=0)
    commission_percent: float = Field(..., ge=0, le=100)
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    product_name: str
    product_image_url: str
    recipient_name: str
    recipient_phone: str
    city: str
    warehouse_number: str
    price: float
    employee_id: int
    is_paid: bool = False


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    ttn_number: Optional[str] = None
    employee_commission: Optional[float] = None
    created_at: datetime
    employee: Employee

    class Config:
        orm_mode = True
