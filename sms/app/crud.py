from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy import select # type: ignore
from . import models, schemas
import pytz # type: ignore
from datetime import datetime, timedelta


async def create_auth_phone(db: AsyncSession, auth_phone: schemas.AuthPhoneCreate):
    seoul_tz = pytz.timezone("Asia/Seoul")
    current_time = datetime.now(seoul_tz)
    expires_at = current_time + timedelta(minutes=10)
    db_auth_phone = models.AuthPhone(
        user_id=auth_phone.user_id,
        phone_number=auth_phone.phone_number,
        verification_code=auth_phone.verification_code,
        verified=False,
        expires_at=expires_at,
    )
    db.add(db_auth_phone)
    await db.commit()
    await db.refresh(db_auth_phone)
    return db_auth_phone


async def get_auth_phone(db: AsyncSession, phone_number: str, verification_code: str):
    result = await db.execute(
        select(models.AuthPhone).where(
            models.AuthPhone.phone_number == phone_number,
            models.AuthPhone.verification_code == verification_code,
            models.AuthPhone.verified == False,
        )
    )
    return result.scalar_one_or_none()


async def verify_auth_phone(db: AsyncSession, auth_phone: models.AuthPhone):
    auth_phone.verified = True
    await db.commit()
    await db.refresh(auth_phone)


async def get_user_by_phone(db: AsyncSession, phone_number: str):
    result = await db.execute(
        select(models.User).where(models.User.phone_number == phone_number)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()


async def create_auth_token(
    db: AsyncSession, user_id: int, token: str, expires_at: datetime
):
    db_auth_token = models.AuthToken(
        user_id=user_id,
        token=token,
        token_type="access",
        created_at=datetime.utcnow(),
        expires_at=expires_at,
    )
    db.add(db_auth_token)
    await db.commit()
    await db.refresh(db_auth_token)
    return db_auth_token


async def get_auth_token(db: AsyncSession, token: str):
    result = await db.execute(
        select(models.AuthToken).where(models.AuthToken.token == token)
    )
    return result.scalar_one_or_none()


async def get_matching_status(db: AsyncSession, user_id: int) -> str:
    result = await db.execute(
        select(models.Match.status).where(
            (models.Match.requester_id == user_id)
            | (models.Match.responder_id == user_id)
        )
    )
    match = result.scalar_one_or_none()
    if match:
        return match.status
    return "none"
