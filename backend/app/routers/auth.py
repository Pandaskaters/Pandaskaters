from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserOut
from app.schemas.driver import DriverRegister
from app.services.auth_service import register_passenger, register_driver, login_user
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register/passenger", response_model=UserOut, status_code=201)
async def register_passenger_endpoint(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await register_passenger(db, data)


@router.post("/register/driver", response_model=UserOut, status_code=201)
async def register_driver_endpoint(data: DriverRegister, db: AsyncSession = Depends(get_db)):
    return await register_driver(db, data)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, data)


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
