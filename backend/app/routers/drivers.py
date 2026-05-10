from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.driver import Driver
from app.models.user import User
from app.schemas.driver import DriverOut, DriverLocationUpdate, DriverStatusUpdate
from app.middleware.auth_middleware import get_current_user, require_driver

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("/nearby", response_model=List[DriverOut])
async def get_nearby_drivers(
    lat: float, lng: float, radius_km: float = 5.0,
    db: AsyncSession = Depends(get_db),
):
    """Return online approved drivers (client-side distance filtering)."""
    from app.models.driver import DriverStatus
    result = await db.execute(
        select(Driver).where(
            Driver.is_online == True,
            Driver.status == DriverStatus.approved,
            Driver.current_lat.is_not(None),
        )
    )
    return result.scalars().all()


@router.get("/me", response_model=DriverOut)
async def get_driver_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_driver),
):
    result = await db.execute(select(Driver).where(Driver.user_id == user.id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    return driver


@router.patch("/me/location")
async def update_location(
    data: DriverLocationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_driver),
):
    result = await db.execute(select(Driver).where(Driver.user_id == user.id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    driver.current_lat = data.lat
    driver.current_lng = data.lng
    await db.commit()
    return {"message": "Location updated"}


@router.patch("/me/status")
async def update_online_status(
    data: DriverStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_driver),
):
    result = await db.execute(select(Driver).where(Driver.user_id == user.id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    driver.is_online = data.is_online
    await db.commit()
    return {"message": f"Status set to {'online' if data.is_online else 'offline'}"}


@router.get("/me/rides")
async def get_driver_rides(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_driver),
):
    from app.models.ride import Ride
    result = await db.execute(select(Driver).where(Driver.user_id == user.id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    rides_result = await db.execute(
        select(Ride).where(Ride.driver_id == driver.id).order_by(Ride.requested_at.desc()).limit(50)
    )
    return rides_result.scalars().all()
