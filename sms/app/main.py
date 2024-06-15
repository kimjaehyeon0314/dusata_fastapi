from fastapi import FastAPI, Depends # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.database import engine, database
from app.routers import auth, matching
from app import models, dependencies
from app.settings import settings  # settings 불러오기


app = FastAPI()

# CORS 설정
origins = [
    "http://localhost",
    "http://localhost:3000",  # React 앱이 실행되는 주소
    "http://127.0.0.1:3000",  # React 앱이 실행되는 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드 목록
    allow_headers=["*"],  # 허용할 HTTP 헤더 목록
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(auth.router)
app.include_router(matching.router)
