# bot/routers/__init__.py

from .register import router as register_router
from .products import router as products_router
# from .cart import router as cart_router
# from .payment import router as payment_router
# from .checkout import router as checkout_router

all_routers = [
    register_router,
    products_router,
    # cart_router,
    # payment_router,
    # checkout_router
]
