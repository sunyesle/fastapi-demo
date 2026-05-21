from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_admin_user
from src.database import get_db_read_session
from src.admin.dashboard.service import dashboard_service
from src.models import User

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])

@router.get("")
async def dashboard(
    admin: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db_read_session),
):
    stats = await dashboard_service.get_dashboard_stats(session)
    recent_orders = await dashboard_service.get_recent_orders(session)
    chart_data = await dashboard_service.get_sales_chart_data(session)
    return {
        "stats": stats,
        "recent_orders": recent_orders,
        "chart_data": chart_data,
    }
