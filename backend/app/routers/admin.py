from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.driver import Driver, DriverStatus
from app.models.ride import Ride, RideStatus
from app.schemas.user import UserOut
from app.schemas.driver import DriverOut
from app.schemas.ride import RideOut
from app.middleware.auth_middleware import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    active_rides_r = await db.execute(
        select(func.count()).where(Ride.status.in_([RideStatus.searching, RideStatus.assigned, RideStatus.in_progress]))
    )
    drivers_online_r = await db.execute(select(func.count()).where(Driver.is_online == True))
    total_users_r = await db.execute(select(func.count()).where(User.role == UserRole.passenger))
    completed_r = await db.execute(select(func.count()).where(Ride.status == RideStatus.completed))
    earnings_r = await db.execute(select(func.sum(Ride.final_fare)).where(Ride.status == RideStatus.completed))

    return {
        "active_rides": active_rides_r.scalar() or 0,
        "drivers_online": drivers_online_r.scalar() or 0,
        "total_users": total_users_r.scalar() or 0,
        "completed_rides": completed_r.scalar() or 0,
        "total_earnings": round(float(earnings_r.scalar() or 0), 2),
    }


@router.get("/users", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.patch("/users/{user_id}/toggle")
async def toggle_user(user_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    await db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}


@router.get("/drivers", response_model=List[DriverOut])
async def list_drivers(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Driver).order_by(Driver.created_at.desc()))
    return result.scalars().all()


@router.patch("/drivers/{driver_id}/approve")
async def approve_driver(driver_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.status = DriverStatus.approved
    await db.commit()
    return {"message": "Driver approved"}


@router.patch("/drivers/{driver_id}/reject")
async def reject_driver(driver_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.status = DriverStatus.rejected
    await db.commit()
    return {"message": "Driver rejected"}


@router.get("/rides", response_model=List[RideOut])
async def list_rides(
    status: str = None, limit: int = 100,
    db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    query = select(Ride).order_by(Ride.requested_at.desc()).limit(limit)
    if status:
        try:
            query = query.where(Ride.status == RideStatus(status))
        except ValueError:
            pass
    result = await db.execute(query)
    return result.scalars().all()
