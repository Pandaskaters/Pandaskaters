from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.driver import DriverStatus, VehicleType


class VehicleCreate(BaseModel):
    plate: str
    brand: str
    model: str
    year: int
    color: str
    vehicle_type: VehicleType


class VehicleOut(BaseModel):
    id: int
    plate: str
    brand: str
    model: str
    year: int
    color: str
    vehicle_type: VehicleType
    photo_url: Optional[str] = None

    model_config = {"from_attributes": True}


class DriverRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    cedula: str
    license_number: str
    vehicle: VehicleCreate


class DriverOut(BaseModel):
    id: int
    user_id: int
    cedula: str
    license_number: str
    status: DriverStatus
    is_online: bool
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    rating: float
    total_rides: int
    total_earnings: float
    vehicle: Optional[VehicleOut] = None

    model_config = {"from_attributes": True}


class DriverLocationUpdate(BaseModel):
    lat: float
    lng: float


class DriverStatusUpdate(BaseModel):
    is_online: bool
