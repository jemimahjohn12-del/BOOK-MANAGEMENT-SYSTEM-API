from fastapi import APIRouter, Depends

from app.api.dependencies import require_admin
from app.domain.entities.user import User

router = APIRouter(tags=["admin"])


@router.get("/admin")
def admin_area(current_user: User = Depends(require_admin)):
    return {"message": f"Welcome, admin {current_user.username}"}