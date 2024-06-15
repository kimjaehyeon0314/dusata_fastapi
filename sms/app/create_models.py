import asyncio
from app.database import engine
from app.models import Base


# init_models 함수는 데이터베이스 연결을 시작하고 Base.metadata.create_all을 호출하여
# 데이터베이스에 테이블을 생성합니다.
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 스크립트가 직접 실행될 때 init_models 함수를 호출하여 데이터베이스를 초기화합니다.
if __name__ == "__main__":
    asyncio.run(init_models())
