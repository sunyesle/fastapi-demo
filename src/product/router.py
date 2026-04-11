from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.product import service as product_service
from src.product.schemas import ProductSchema, ProductCreate
from src.product.service import product_service
from src.models.product import Product


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductSchema, status_code=201)
async def create(
    product_create: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
) -> Product:
    return await product_service.create(session, product_create)
