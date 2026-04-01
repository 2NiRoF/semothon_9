from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# TODO: 담당 팀원이 구현
# POST /auth/register  — 회원가입
# POST /auth/login     — 로그인 (JWT 토큰 반환)
# POST /auth/logout    — 로그아웃
