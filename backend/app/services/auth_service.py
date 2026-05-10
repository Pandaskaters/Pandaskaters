from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.driver import Driver, Vehicle
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.schemas.driver import DriverRegister
from app.utils.password_handler import hash_password, verify_password
from app.utils.jwt_handler import create_access_token


async def register_passenger(db: AsyncSession, data: UserRegister) -> User:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=UserRole.passenger,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def register_driver(db: AsyncSession, data: DriverRegister) -> User:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=UserRole.driver,
    )
    db.add(user)
    await db.flush()

    driver = Driver(
        user_id=user.id,
        cedula=data.cedula,
        license_number=data.license_number,
    )
    db.add(driver)
    await db.flush()

    vehicle = Vehicle(
        driver_id=driver.id,
        plate=data.vehicle.plate,
        brand=data.vehicle.brand,
        model=data.vehicle.model,
        year=data.vehicle.year,
        color=data.vehicle.color,
        vehicle_type=data.vehicle.vehicle_type,
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, data: UserLogin) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=user)
