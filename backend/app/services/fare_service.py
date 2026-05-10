import math
from app.config import settings
from app.models.ride import ServiceType
from app.schemas.ride import FareEstimate


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km between two coordinates."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_duration(distance_km: float, service_type: ServiceType) -> float:
    """Estimate duration in minutes based on distance and service type."""
    avg_speed = {
        ServiceType.economy: 35,
        ServiceType.premium: 40,
        ServiceType.moto: 45,
    }.get(service_type, 35)
    return (distance_km / avg_speed) * 60


def calculate_fare(distance_km: float, service_type: ServiceType) -> float:
    fares = {
        ServiceType.economy: (settings.BASE_FARE_ECONOMY, settings.PER_KM_ECONOMY),
        ServiceType.premium: (settings.BASE_FARE_PREMIUM, settings.PER_KM_PREMIUM),
        ServiceType.moto: (settings.BASE_FARE_MOTO, settings.PER_KM_MOTO),
    }
    base, per_km = fares.get(service_type, (settings.BASE_FARE_ECONOMY, settings.PER_KM_ECONOMY))
    return round(base + (per_km * distance_km), 2)


def get_fare_estimate(
    origin_lat: float, origin_lng: float,
    dest_lat: float, dest_lng: float,
    service_type: ServiceType,
) -> FareEstimate:
    distance = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    duration = estimate_duration(distance, service_type)
    fare = calculate_fare(distance, service_type)
    return FareEstimate(
        service_type=service_type,
        distance_km=round(distance, 2),
        duration_min=round(duration, 1),
        fare=fare,
    )
