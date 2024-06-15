import enum
from pydantic import BaseModel, Field # type: ignore
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class MbtiEnum(str, enum.Enum):
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    INFJ = "INFJ"
    INTJ = "INTJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    INFP = "INFP"
    INTP = "INTP"
    ESTP = "ESTP"
    ESFP = "ESFP"
    ENFP = "ENFP"
    ENTP = "ENTP"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ENFJ = "ENFJ"
    ENTJ = "ENTJ"


class AnimalEnum(str, enum.Enum):
    dog = "강아지상"
    cat = "고양이상"
    mouse = "햄스터상"
    lion = "사자상"
    tiger = "호랑이상" 
    bear = "곰상"
    rabbit = "토끼상"
    wolf ="늑대상"
    monkey = "원숭이상"


class MatchingStatusEnum(str, enum.Enum):
    none = "none"
    waiting = "waiting"
    accept = "accept"
    reject = "reject"


class UserCreateResponse(BaseModel):
    id: int
    phone_number: str
    user_name: str
    user_kakao: str
    major: str
    student_number: int
    gender: GenderEnum
    hobby: str
    mbti: MbtiEnum
    smoke: bool
    animal: AnimalEnum
    introduce: str
    auth_token: Optional[str] = None  # auth_token 필드 추가

    class Config:
        orm_mode = True
        from_attributes = True


class UserBase(BaseModel):
    phone_number: str
    user_name: str
    user_kakao: str
    major: str
    student_number: int
    gender: GenderEnum
    hobby: str
    mbti: MbtiEnum
    smoke: bool
    animal: AnimalEnum
    introduce: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class AuthPhoneBase(BaseModel):
    phone_number: str
    verification_code: str
    verified: bool = False


class AuthPhoneCreate(AuthPhoneBase):
    user_id: Optional[int]
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(minutes=10)
    )


class AuthPhoneResponse(BaseModel):
    success: bool


class PhoneNumberRequest(BaseModel):
    phone_number: str


class PhoneAuthCheckRequest(BaseModel):
    phone_number: str
    verification_code: str


class VerificationResponse(BaseModel):
    verification_success: bool
    is_registered: bool
    auth_token: str
    redirect: str


class UserResponse(BaseModel):
    id: int
    animal: str
    introduce: str
    smoke: bool
    user_name: str
    user_kakao: str

    class Config:
        orm_mode = True


class MatchRequest(BaseModel):
    partner_id: int


class MatchResponse(BaseModel):
    match_id: int
    accept: bool
