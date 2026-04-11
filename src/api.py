from fastapi import APIRouter

from src.category.router import router as category_router
from src.product.router import router as product_router

router = APIRouter()

router.include_router(category_router)
router.include_router(product_router)
