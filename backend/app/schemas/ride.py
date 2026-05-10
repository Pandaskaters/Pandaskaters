from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.ride import RideStatus, ServiceType


class RideRequest(BaseModel):
    origin_address: str
    origin_lat: float
    origin_lng: float
    destination_address: str
    destination_lat: float
    destination_lng: float
    service_type: ServiceType = ServiceType.economy
    notes: Optional[str] = None


class FareEstimate(BaseModel):
    service_type: ServiceType
    distance_km: float
    duration_min: float
    fare: float


class RideOut(BaseModel):
    id: int
    passenger_id: int
    driver_id: Optional[int] = None
    origin_address: str
    origin_lat: float
    origin_lng: float
    destination_address: str
    destination_lat: float
    destination_lng: float
    service_type: ServiceType
    status: RideStatus
    estimated_distance_km: Optional[float] = None
    estimated_duration_min: Optional[float] = None
    estimated_fare: Optional[float] = None
    final_fare: Optional[float] = None
    requested_at: datetime
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RideStatusUpdate(BaseModel):
    status: RideStatus
    cancellation_reason: Optional[str] = None


class RideRatingCreate(BaseModel):
    driver_rating: Optional[float] = None
    passenger_rating: Optional[float] = None
    passenger_comment: Optional[str] = None
    driver_comment: Optional[str] = None
