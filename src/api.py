from fastapi import APIRouter

from src.category.router import router as category_router

router = APIRouter()

router.include_router(category_router)
