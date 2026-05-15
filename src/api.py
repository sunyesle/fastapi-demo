from fastapi import APIRouter

from src.category.router import router as category_router
from src.product.router import router as product_router
from src.user.router import router as user_router
from src.auth.router import router as auth_router
from src.cart.router import router as cart_router
from src.order.router import router as order_router

router = APIRouter()

router.include_router(category_router)
router.include_router(product_router)
router.include_router(user_router)
router.include_router(auth_router)
router.include_router(cart_router)
router.include_router(order_router)
