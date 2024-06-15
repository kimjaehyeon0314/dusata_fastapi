from mailbox import Message
from fastapi import APIRouter, Depends, HTTPException, status, Body # type: ignore
import pytz # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from pydantic import BaseModel # type: ignore
from jose import jwt # type: ignore
import random
from datetime import datetime, timedelta
from .. import schemas, crud
from ..database import get_db
from ..settings import settings  # 환경 변수 설정 파일 가져오기
from ..dependencies import get_current_user
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
import logging

router = APIRouter()

API_KEY = "NCSL0ENUGIAOQNEV"
API_SECRET = "BVJJOKUR57T0ZJN0VIRQ8BXW07WM9XEF"
SENDER_NUMBER = "01098415804"
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
TIMEZONE = pytz.timezone("Asia/Seoul")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(TIMEZONE) + expires_delta
    else:
        expire = datetime.now(TIMEZONE) + timedelta(minutes=720)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


def send_sms(phone_number: str, verification_code: str):
    params = {
        "type": "sms",
        "to": phone_number,
        "from": SENDER_NUMBER,
        "text": f"인증번호는 {verification_code}입니다.",
    }
    cool = Message(API_KEY, API_SECRET)
    try:
        response = cool.send(params)
        print("Success Count : %s" % response["success_count"])
        print("Error Count : %s" % response["error_count"])
        print("Group ID : %s" % response["group_id"])

        if "error_list" in response:
            print("Error List : %s" % response["error_list"])
        return response["success_count"] > 0

    except CoolsmsException as e: # type: ignore
        print("Error Code : %s" % e.code)
        print("Error Message : %s" % e.msg)
        return False


class PhoneNumberRequest(BaseModel):
    phone_number: str


@router.post("/auth/phone", response_model=schemas.AuthPhoneResponse)
async def send_verification_code(
    request: PhoneNumberRequest, db: AsyncSession = Depends(get_db)
):
    phone_number = request.phone_number
    verification_code = str(random.randint(100000, 999999))  # 6자리 랜덤 숫자 생성

    user = await crud.get_user_by_phone(db, phone_number)
    user_id = user.id if user else None

    auth_phone = schemas.AuthPhoneCreate(
        user_id=user_id,
        phone_number=phone_number,
        verification_code=verification_code,
        verified=False,
    )
    await crud.create_auth_phone(db=db, auth_phone=auth_phone)

    if send_sms(phone_number, verification_code):
        return {"success": True}
    else:
        raise HTTPException(status_code=500, detail="Failed to send SMS")


@router.post("/auth/phone-check", response_model=schemas.VerificationResponse)
async def check_verification_code(
    request: schemas.PhoneAuthCheckRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    phone_number = request.phone_number
    verification_code = request.verification_code
    auth_phone = await crud.get_auth_phone(db, phone_number, verification_code)
    if not auth_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code"
        )

    await crud.verify_auth_phone(db, auth_phone)

    user = await crud.get_user_by_phone(db, phone_number)
    is_registered = user is not None

    if is_registered:
        access_token, expires_at = create_access_token(data={"sub": str(user.id)})
        await crud.create_auth_token(db, user.id, access_token, expires_at)
        return schemas.VerificationResponse(
            verification_success=True,
            is_registered=True,
            auth_token=access_token,
            redirect="/main",  # 메인 페이지로 리디렉션
        )
    else:
        return schemas.VerificationResponse(
            verification_success=True,
            is_registered=False,
            auth_token="",
            redirect="/user/register",  # 회원가입 페이지로 리디렉션
        )

# 여기서 새로운 엔드포인트를 추가합니다.
@router.post("/user/register/check")
async def check_user_registration(
    phone_number: PhoneNumberRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    existing_user = await crud.get_user_by_phone(db, phone_number.phone_number)
    return {"is_registered": existing_user is not None}

@router.post("/user/register", response_model=schemas.UserCreateResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 중복 가입 여부 확인
    existing_user = await crud.get_user_by_phone(db, user.phone_number)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 사용자입니다.",
        )

    # 데이터 유효성 검사
    user_dict = user.dict()
    required_fields = [
        "phone_number",
        "user_name",
        "user_kakao",
        "major",
        "student_number",
        "gender",
        "hobby",
        "mbti",
        "smoke",
        "animal",
        "introduce",
    ]
    for field in required_fields:
        if field not in user_dict or user_dict[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바른 값을 넣어주세요",
            )

    # 사용자 생성
    try:
        new_user = await crud.create_user(db, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation error: {str(e)}",
        )

    # 토큰 생성
    access_token, expires_at = create_access_token(data={"sub": str(new_user.id)})

    # Pydantic 모델로 변환
    new_user_data = schemas.UserCreateResponse.from_orm(new_user)

    # 응답 데이터에 토큰 추가
    response_data = new_user_data.dict()
    response_data.update({"auth_token": access_token})

    return response_data


@router.get("/user/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: schemas.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
