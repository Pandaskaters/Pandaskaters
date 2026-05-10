from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.models.ride import Ride, RideStatus, RideRating
from app.models.driver import Driver
from app.models.user import User
from app.schemas.ride import RideRequest, RideOut, RideStatusUpdate, FareEstimate, RideRatingCreate
from app.services.fare_service import get_fare_estimate
from app.middleware.auth_middleware import get_current_user, require_driver
from app.routers.websocket import manager

router = APIRouter(prefix="/rides", tags=["Rides"])


@router.post("/estimate", response_model=List[FareEstimate])
async def estimate_fare(
    origin_lat: float, origin_lng: float,
    dest_lat: float, dest_lng: float,
):
    from app.models.ride import ServiceType
    return [
        get_fare_estimate(origin_lat, origin_lng, dest_lat, dest_lng, st)
        for st in ServiceType
    ]


@router.post("/request", response_model=RideOut, status_code=201)
async def request_ride(
    data: RideRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    estimate = get_fare_estimate(
        data.origin_lat, data.origin_lng,
        data.destination_lat, data.destination_lng,
        data.service_type,
    )
    ride = Ride(
        passenger_id=user.id,
        origin_address=data.origin_address,
        origin_lat=data.origin_lat,
        origin_lng=data.origin_lng,
        destination_address=data.destination_address,
        destination_lat=data.destination_lat,
        destination_lng=data.destination_lng,
        service_type=data.service_type,
        estimated_distance_km=estimate.distance_km,
        estimated_duration_min=estimate.duration_min,
        estimated_fare=estimate.fare,
        notes=data.notes,
    )
    db.add(ride)
    await db.commit()
    await db.refresh(ride)
    await manager.broadcast({"type": "new_ride", "ride_id": ride.id, "service": data.service_type.value})
    return ride


@router.get("/active", response_model=List[RideOut])
async def get_active_rides(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    active_statuses = [RideStatus.searching, RideStatus.assigned, RideStatus.driver_arriving, RideStatus.in_progress]
    result = await db.execute(
        select(Ride).where(
            Ride.passenger_id == user.id,
            Ride.status.in_(active_statuses)
        )
    )
    return result.scalars().all()


@router.get("/history", response_model=List[RideOut])
async def get_ride_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Ride)
        .where(Ride.passenger_id == user.id)
        .order_by(Ride.requested_at.desc())
        .limit(50)
    )
    return result.scalars().all()


@router.get("/{ride_id}", response_model=RideOut)
async def get_ride(ride_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride


@router.patch("/{ride_id}/status", response_model=RideOut)
async def update_ride_status(
    ride_id: int,
    data: RideStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    now = datetime.now(timezone.utc)
    ride.status = data.status
    if data.cancellation_reason:
        ride.cancellation_reason = data.cancellation_reason
    if data.status == RideStatus.in_progress:
        ride.started_at = now
    elif data.status == RideStatus.completed:
        ride.completed_at = now
        ride.final_fare = ride.estimated_fare

    await db.commit()
    await db.refresh(ride)
    await manager.broadcast({"type": "ride_status", "ride_id": ride_id, "status": data.status.value})
    return ride


@router.post("/driver/accept/{ride_id}", response_model=RideOut)
async def accept_ride(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_driver),
):
    driver_result = await db.execute(select(Driver).where(Driver.user_id == user.id))
    driver = driver_result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    result = await db.execute(select(Ride).where(Ride.id == ride_id, Ride.status == RideStatus.searching))
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not available")

    ride.driver_id = driver.id
    ride.status = RideStatus.assigned
    ride.assigned_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ride)
    await manager.broadcast({"type": "ride_accepted", "ride_id": ride_id, "driver_id": driver.id})
    return ride


@router.post("/{ride_id}/rate")
async def rate_ride(
    ride_id: int,
    data: RideRatingCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Ride).where(Ride.id == ride_id))
    ride = result.scalar_one_or_none()
    if not ride or ride.status != RideStatus.completed:
        raise HTTPException(status_code=400, detail="Ride not found or not completed")

    rating = RideRating(
        ride_id=ride_id,
        driver_rating=data.driver_rating,
        passenger_rating=data.passenger_rating,
        passenger_comment=data.passenger_comment,
        driver_comment=data.driver_comment,
    )
    db.add(rating)
    await db.commit()
    return {"message": "Rating submitted"}
