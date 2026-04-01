"""
앱 시작 시 초기 데이터를 DB에 삽입합니다.
이미 데이터가 있으면 삽입하지 않습니다.
"""
from database import SessionLocal
from models import Mission, User

INITIAL_MISSIONS = [
    {"title": "텀블러 사용하기",   "type": "텀블러",     "description": "일회용 컵 대신 텀블러를 사용해 플라스틱을 줄여요."},
    {"title": "쓰레기 줍기",       "type": "쓰레기 줍기", "description": "산책하며 주변 쓰레기를 주워 깨끗한 환경을 만들어요."},
    {"title": "분리수거 실천하기",  "type": "분리수거",    "description": "올바른 분리수거로 재활용률을 높여요."},
    {"title": "플로깅 챌린지",     "type": "플로깅",     "description": "조깅하면서 쓰레기도 줍는 일석이조 활동이에요."},
    {"title": "해안 정화 활동",    "type": "해안 정화",   "description": "해안가 쓰레기를 수거해 바다 생태계를 보호해요."},
]


def seed_missions():
    db = SessionLocal()
    try:
        if db.query(Mission).count() == 0:
            for data in INITIAL_MISSIONS:
                db.add(Mission(**data, max_participants=4))
            db.commit()
    finally:
        db.close()


TEST_USERS = [
    {"id": 1, "username": "에코냥이",   "email": "user1@test.com"},
    {"id": 2, "username": "초록곰돌이", "email": "user2@test.com"},
    {"id": 3, "username": "지구지킴이", "email": "user3@test.com"},
    {"id": 4, "username": "플로깅왕",   "email": "user4@test.com"},
]


def seed_test_user():
    """테스트용 유저 4명 생성. auth 구현 전 임시 사용."""
    db = SessionLocal()
    try:
        for u in TEST_USERS:
            if not db.query(User).filter(User.id == u["id"]).first():
                db.add(User(id=u["id"], username=u["username"], email=u["email"], hashed_password="temp"))
        db.commit()
    finally:
        db.close()
