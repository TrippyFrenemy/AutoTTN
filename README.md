# Order Management System with Nova Poshta Integration

A FastAPI-based web application for managing orders and employees with seamless integration with Nova Poshta delivery services in Ukraine. The system provides comprehensive order tracking, employee management, and delivery coordination features.

## Features

### Order Management
- Create and track orders with detailed product information
- Automated Nova Poshta waybill generation
- Real-time delivery status tracking
- Order packing queue management
- Payment status tracking

### Employee Management
- Track employee performance metrics
- Commission-based payment system
- Employee activity status management
- Monthly statistics and performance analysis

### Nova Poshta Integration
- City and warehouse search
- Automated shipping cost calculation
- TTN (waybill) generation and tracking
- Recipient data management
- Warehouse selection with detailed information

### Admin Features
- Secure admin panel
- Comprehensive order overview
- Revenue tracking
- Performance analytics
- Employee commission management

## Technical Stack

- **Backend Framework**: FastAPI
- **Database**: SQLAlchemy with async support
- **Template Engine**: Jinja2
- **Authentication**: Custom session-based auth
- **API Integration**: Nova Poshta API v2.0
- **Frontend**: HTML, CSS, JavaScript

## Project Structure

```
├── src/
│   ├── routers/
│   │   ├── admin_router.py      # Admin panel routes
│   │   ├── auth_router.py       # Authentication routes
│   │   ├── employees_router.py  # Employee management
│   │   ├── nova_poshta_router.py# Nova Poshta API integration
│   │   └── orders_router.py     # Order management
│   ├── service/
│   │   ├── auth_service.py      # Authentication logic
│   │   └── nova_post.py         # Nova Poshta API client
│   ├── templates/               # HTML templates
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   └── schemas.py              # Pydantic models
└── main.py                     # Application entry point
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings:
   - Database credentials
   - Nova Poshta API key
   - Admin credentials
   - Redis configuration (if using caching)

4. Initialize the database:
   ```bash
   alembic upgrade head
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Database Models

### Employee Model
- Basic information (name, status)
- Payment details (hourly rate, commission percentage)
- Performance tracking (orders, sales)

### Order Model
- Product details
- Delivery information
- Payment status
- Employee assignment
- Nova Poshta tracking data

### DailyCommission Model
- Daily performance tracking
- Commission calculations
- Sales statistics

## API Endpoints

### Admin Routes
- `/admin/` - Admin dashboard
- `/admin/orders/` - Order management

### Employee Routes
- `/employees/` - Employee management
- `/employees/{employee_id}/stats` - Employee statistics
- `/employees/{employee_id}/toggle` - Toggle employee status

### Order Routes
- `/order-form` - New order creation
- `/orders/` - Order list
- `/orders/{order_id}/toggle-packed` - Update packing status
- `/orders/{order_id}/toggle-payment` - Update payment status

### Nova Poshta Routes
- `/api/np/settlements` - City search
- `/api/np/warehouses/{city_ref}` - Warehouse search
- `/api/np/delivery-price` - Shipping cost calculation
- `/api/np/tracking/{ttn}` - Package tracking

## Security

- Session-based authentication
- Secure cookie handling
- Role-based access control
- Request validation
- CORS configuration

## User Interface

The application provides a responsive web interface with:
- Clean, intuitive order forms
- Real-time city and warehouse search
- Dynamic delivery cost calculation
- Employee performance dashboards
- Order tracking and management interfaces

## Error Handling

- Comprehensive API error responses
- User-friendly error messages
- Input validation
- Nova Poshta API error handling
