import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from models import Mission  # noqa: F401 — 테이블 생성에 필요
from routers import auth, users, missions, matches, posts
from seed import seed_missions, seed_test_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시
    os.makedirs("uploads", exist_ok=True)   # 업로드 폴더 자동 생성
    Base.metadata.create_all(bind=engine)   # DB 테이블 생성
    seed_missions()                          # 초기 미션 데이터 삽입
    seed_test_user()                         # 테스트 유저 생성 (auth 구현 전 임시)
    yield
    # 서버 종료 시 (필요하면 여기에 정리 코드 추가)


app = FastAPI(title="세모톤 API", lifespan=lifespan)

# CORS — 프론트(React) 에서 호출 가능하도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 이미지 정적 파일 서빙
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 라우터 등록
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(missions.router)
app.include_router(matches.router)
app.include_router(posts.router)


@app.get("/")
def root():
    return {"message": "세모톤 API 서버가 실행 중입니다."}
