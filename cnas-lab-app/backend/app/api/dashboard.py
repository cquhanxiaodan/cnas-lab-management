from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth import get_current_user
from app.services.dashboard import get_dashboard_stats
from app.models.models import User


router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard_stats(db)


@router.get("/warnings")
def get_warnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = get_dashboard_stats(db)
    return {"warnings": stats["warnings"]}
