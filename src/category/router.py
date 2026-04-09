from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.category.schemas import CategoryCreate, CategorySchema
from src.category.service import category_service
from src.database import get_db_session
from src.models.category import Category


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategorySchema, status_code=201)
def create(
    category_create: CategoryCreate,
    session: Session = Depends(get_db_session),
) -> Category:
    return category_service.create(session, category_create)
