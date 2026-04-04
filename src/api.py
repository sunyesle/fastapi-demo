from fastapi import APIRouter

from src.item.endpoints import router as item_router


router = APIRouter(prefix="/v1")

router.include_router(item_router)
