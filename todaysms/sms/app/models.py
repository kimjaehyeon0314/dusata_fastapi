from sqlalchemy import ( # type: ignore
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    Enum,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy.sql import func # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from .database import Base
import enum
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(11), unique=True, index=True)
    user_name = Column(String(50))
    user_kakao = Column(String(50))
    major = Column(String(50))
    student_number = Column(Integer)
    gender = Column(Enum("male", "female", name="gender"))
    hobby = Column(String(255))  # ENUM -> VARCHAR로 변경
    mbti = Column(
        Enum(
            "ISTJ",
            "ISFJ",
            "INFJ",
            "INTJ",
            "ISTP",
            "ISFP",
            "INFP",
            "INTP",
            "ESTP",
            "ESFP",
            "ENFP",
            "ENTP",
            "ESTJ",
            "ESFJ",
            "ENFJ",
            "ENTJ",
            name="mbti",
        )
    )
    smoke = Column(Boolean)
    
    
    
    
    animal = Column(
        Enum(
            "강아지상",
            "고양이상",
            "햄스터상",
            "사자상",
            "호랑이상",
            "곰상",
            "토끼상",
            "늑대상",
            "원숭이상",
            name="animal",
        )
    )
    introduce = Column(String(200))
    matching_status = Column(Enum(MatchingStatusEnum), default=MatchingStatusEnum.none)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    auth_phones = relationship("AuthPhone", back_populates="user")


class Match(Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum("reject", "waiting", "accept", "none"), nullable=False, default="none"
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    requester = relationship("User", foreign_keys=[requester_id])
    responder = relationship("User", foreign_keys=[responder_id])


class AuthPhone(Base):
    __tablename__ = "auth_phone"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone_number = Column(String(11), index=True)
    verification_code = Column(String(6))
    verified = Column(Boolean, default=False)
    expires_at = Column(DateTime, default=datetime.utcnow() + timedelta(minutes=10))

    user = relationship("User", back_populates="auth_phones")


class AuthToken(Base):
    __tablename__ = "auth_token"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_type = Column(Enum("access", "refresh"), nullable=False)
    token = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
