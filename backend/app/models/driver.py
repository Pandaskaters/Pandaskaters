from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class VehicleType(str, enum.Enum):
    economy = "economy"
    premium = "premium"
    moto = "moto"


class DriverStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    plate = Column(String(20), unique=True, nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(30), nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    photo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    driver = relationship("Driver", back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    license_number = Column(String(50), nullable=False)
    license_photo_url = Column(String(500), nullable=True)
    status = Column(Enum(DriverStatus), default=DriverStatus.pending)
    is_online = Column(Boolean, default=False)
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    rating = Column(Float, default=5.0)
    total_rides = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="driver_profile")
    vehicle = relationship("Vehicle", back_populates="driver", uselist=False)
    rides = relationship("Ride", back_populates="driver", foreign_keys="Ride.driver_id")
