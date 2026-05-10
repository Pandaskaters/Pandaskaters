from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RideStatus(str, enum.Enum):
    searching = "searching"
    assigned = "assigned"
    driver_arriving = "driver_arriving"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class ServiceType(str, enum.Enum):
    economy = "economy"
    premium = "premium"
    moto = "moto"


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)

    origin_address = Column(String(300), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)

    destination_address = Column(String(300), nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)

    service_type = Column(Enum(ServiceType), nullable=False, default=ServiceType.economy)
    status = Column(Enum(RideStatus), default=RideStatus.searching)

    estimated_distance_km = Column(Float, nullable=True)
    estimated_duration_min = Column(Float, nullable=True)
    estimated_fare = Column(Float, nullable=True)
    final_fare = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    cancellation_reason = Column(String(200), nullable=True)

    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    passenger = relationship("User", back_populates="rides_as_passenger", foreign_keys=[passenger_id])
    driver = relationship("Driver", back_populates="rides", foreign_keys=[driver_id])
    rating = relationship("RideRating", back_populates="ride", uselist=False)


class RideRating(Base):
    __tablename__ = "ride_ratings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), unique=True, nullable=False)
    passenger_rating = Column(Float, nullable=True)
    driver_rating = Column(Float, nullable=True)
    passenger_comment = Column(Text, nullable=True)
    driver_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ride = relationship("Ride", back_populates="rating")
