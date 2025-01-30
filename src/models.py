from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, Date
from datetime import datetime

from sqlalchemy.orm import relationship

from .database import Base


class DailyCommission(Base):
    __tablename__ = "daily_commissions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date, index=True)
    total_commission = Column(Float, default=0)
    total_orders = Column(Integer, default=0)
    total_sales = Column(Float, default=0)

    employee = relationship("Employee", back_populates="daily_commissions")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    hourly_rate = Column(Float)  # Часовая ставка
    commission_percent = Column(Float)  # Процент от продаж
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с заказами
    orders = relationship("Order", back_populates="employee")

    daily_commissions = relationship("DailyCommission", back_populates="employee")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_image_url = Column(String)
    recipient_name = Column(String)
    recipient_phone = Column(String)
    city_ref = Column(String)  # Ref города из НП
    warehouse_ref = Column(String)  # Ref отделения из НП
    ttn_number = Column(String, nullable=True)  # Номер ТТН
    price = Column(Float)
    is_paid = Column(Boolean, default=False)
    is_packed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с сотрудником
    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", back_populates="orders")

    # Расчетные поля для сотрудника
    employee_commission = Column(Float)  # Сумма комиссии для сотрудника

    commission_date = Column(Date, default=datetime.utcnow().date)
