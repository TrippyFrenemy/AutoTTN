from .auth_router import router as auth_router
from .admin_router import router as admin_router
from .orders_router import router as orders_router
from .employees_router import router as employees_router
from .nova_poshta_router import router as nova_poshta_router

__all__ = [
    'auth_router',
    'admin_router',
    'orders_router',
    'employees_router',
    'nova_poshta_router'
]