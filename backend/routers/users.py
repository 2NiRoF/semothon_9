from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

# TODO: 담당 팀원이 구현
# GET    /users/me                    — 내 프로필 조회
# PUT    /users/me                    — 프로필 수정
# DELETE /users/me                    — 회원탈퇴
# GET    /users/me/records            — 내 활동 기록
# DELETE /users/me/records/{id}       — 기록 삭제
# GET    /users/me/points             — 내 포인트 조회
# POST   /users/me/points             — 포인트 수령
