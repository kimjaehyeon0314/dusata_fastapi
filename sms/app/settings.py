from pydantic_settings import BaseSettings # type: ignore


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 12시간
    timezone: str = "Asia/Seoul"

    class Config:
        env_file = ".env"


settings = Settings()
