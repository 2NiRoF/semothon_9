from fastapi import APIRouter, Form, HTTPException
from database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), name: str = Form(...)):
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password, name, points) VALUES (?, ?, ?, 0)", (username, password, name))
        db.commit()
        return {"message": "회원가입 성공"}
    except:
        raise HTTPException(status_code=400, detail="중복된 아이디이거나 오류가 발생했습니다.")

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호가 틀렸습니다.")
    return {"message": "로그인 성공", "user": {"username": user["username"], "name": user["name"]}}
