#!/usr/bin/env python3
"""
Create demo users for testing.
Run: python create_demo_users.py
"""
import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.driver import Driver, Vehicle, DriverStatus, VehicleType
from app.utils.password_handler import hash_password
from sqlalchemy import select


async def create_demo_data():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Check if demo data exists
        res = await db.execute(select(User).where(User.email == 'passenger@demo.com'))
        if res.scalar_one_or_none():
            print("✓ Demo data already exists")
            return

        # Passenger
        passenger = User(
            name="Ana González",
            email="passenger@demo.com",
            phone="0991234567",
            hashed_password=hash_password("demo123"),
            role=UserRole.passenger,
            is_active=True,
            is_verified=True,
            rating=4.8,
            total_rides=12,
        )
        db.add(passenger)

        # Driver user
        driver_user = User(
            name="Carlos Mendoza",
            email="driver@demo.com",
            phone="0987654321",
            hashed_password=hash_password("demo123"),
            role=UserRole.driver,
            is_active=True,
            is_verified=True,
            rating=4.9,
            total_rides=87,
        )
        db.add(driver_user)
        await db.flush()

        # Driver profile
        driver = Driver(
            user_id=driver_user.id,
            cedula="1234567890",
            license_number="LIC-001234",
            status=DriverStatus.approved,
            is_online=False,
            current_lat=4.7110,
            current_lng=-74.0721,
            rating=4.9,
            total_rides=87,
            total_earnings=652.40,
        )
        db.add(driver)
        await db.flush()

        # Vehicle
        vehicle = Vehicle(
            driver_id=driver.id,
            plate="ABC-1234",
            brand="Toyota",
            model="Corolla",
            year=2021,
            color="Blanco",
            vehicle_type=VehicleType.economy,
        )
        db.add(vehicle)
        await db.commit()

        print("✅ Demo users created:")
        print("  👤 Pasajero: passenger@demo.com / demo123")
        print("  🚗 Conductor: driver@demo.com / demo123")
        print("  🛡️  Admin: admin@pandaskaters.com / admin123")


if __name__ == "__main__":
    asyncio.run(create_demo_data())
