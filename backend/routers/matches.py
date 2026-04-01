import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Match, MatchParticipant, Mission, Post, React
from schemas import (
    MatchCreate, MatchResponse, ParticipantResponse,
    PostResponse, ReactCreate, ReactUpdate, ReactResponse,
)

router = APIRouter(prefix="/matches", tags=["matches"])

UPLOAD_DIR = "uploads"


# ── 임시 인증 헬퍼 ──────────────────────────────────────
# TODO: auth 팀원이 JWT 구현하면 이 함수를 교체하세요.
# 지금은 테스트용으로 user_id를 헤더로 직접 받습니다.
from fastapi import Header

def get_current_user_id(x_user_id: int = Header(..., description="현재 로그인 유저 ID")) -> int:
    return x_user_id


# ── /matches ────────────────────────────────────────────

@router.post("", response_model=MatchResponse, status_code=201)
def create_or_join_match(
    body: MatchCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    매칭 요청.
    - 해당 미션에 자리가 있는 매치(waiting, 4명 미만)가 있으면 그 방에 참여
    - 없으면 새 매치 생성
    """
    mission = db.query(Mission).filter(Mission.id == body.mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다.")

    # 이미 참여 중인지 확인
    already = (
        db.query(MatchParticipant)
        .join(Match)
        .filter(
            Match.mission_id == body.mission_id,
            Match.status.in_(["waiting", "in_progress"]),
            MatchParticipant.user_id == user_id,
        )
        .first()
    )
    if already:
        raise HTTPException(status_code=400, detail="이미 이 미션에 참여 중입니다.")

    # 자리 있는 매치 찾기
    available_match = None
    waiting_matches = (
        db.query(Match)
        .filter(Match.mission_id == body.mission_id, Match.status == "waiting")
        .all()
    )
    for match in waiting_matches:
        if len(match.participants) < mission.max_participants:
            available_match = match
            break

    # 없으면 새로 생성
    if not available_match:
        available_match = Match(mission_id=body.mission_id, status="waiting")
        db.add(available_match)
        db.flush()

    # 참여자 추가
    participant = MatchParticipant(match_id=available_match.id, user_id=user_id)
    db.add(participant)

    # 정원이 찼으면 in_progress로 변경
    db.flush()
    db.refresh(available_match)
    if len(available_match.participants) >= mission.max_participants:
        available_match.status = "in_progress"

    db.commit()
    db.refresh(available_match)

    return _build_match_response(available_match, db)


@router.get("/me", response_model=Optional[MatchResponse])
def get_my_active_match(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """현재 유저가 참여 중인 활성 매치 반환. 없으면 null."""
    participant = (
        db.query(MatchParticipant)
        .join(Match)
        .filter(
            MatchParticipant.user_id == user_id,
            Match.status.in_(["waiting", "in_progress"]),
        )
        .first()
    )
    if not participant:
        return None
    return _build_match_response(participant.match, db)


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """매칭 상세 조회 (참여자 목록, 상태)."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="매칭을 찾을 수 없습니다.")
    return _build_match_response(match, db)


@router.delete("/{match_id}", status_code=204)
def leave_match(
    match_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """미션 중도 포기 — 참여자 목록에서 제거."""
    participant = (
        db.query(MatchParticipant)
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id == user_id,
        )
        .first()
    )
    if not participant:
        raise HTTPException(status_code=404, detail="해당 매칭에 참여하고 있지 않습니다.")

    db.delete(participant)
    db.commit()


# ── /matches/{id}/posts ──────────────────────────────────

@router.get("/{match_id}/posts", response_model=list[PostResponse])
def get_posts(match_id: int, db: Session = Depends(get_db)):
    """매칭 내 인증 목록 조회."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="매칭을 찾을 수 없습니다.")

    posts = db.query(Post).filter(Post.match_id == match_id).all()
    return [_build_post_response(p) for p in posts]


@router.post("/{match_id}/posts", response_model=PostResponse, status_code=201)
async def create_post(
    match_id: int,
    comment: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """인증 사진 + 코멘트 업로드."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="매칭을 찾을 수 없습니다.")

    # 참여자인지 확인
    is_participant = any(p.user_id == user_id for p in match.participants)
    if not is_participant:
        raise HTTPException(status_code=403, detail="해당 매칭의 참여자가 아닙니다.")

    # 이미지 저장
    image_url = None
    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/uploads/{filename}"

    post = Post(
        match_id=match_id,
        user_id=user_id,
        image_url=image_url,
        comment=comment,
        status="pending",
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return _build_post_response(post)


@router.delete("/{match_id}/posts/{post_id}", status_code=204)
def delete_post(
    match_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """인증 삭제 (본인 글만 삭제 가능)."""
    post = db.query(Post).filter(Post.id == post_id, Post.match_id == match_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="인증을 찾을 수 없습니다.")
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인의 인증만 삭제할 수 있습니다.")

    db.delete(post)
    db.commit()


# ── /matches/{id}/posts/{post_id}/reacts ────────────────

@router.get("/{match_id}/posts/{post_id}/reacts", response_model=list[ReactResponse])
def get_reacts(match_id: int, post_id: int, db: Session = Depends(get_db)):
    """인증에 달린 반응 목록."""
    post = db.query(Post).filter(Post.id == post_id, Post.match_id == match_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="인증을 찾을 수 없습니다.")

    reacts = db.query(React).filter(React.post_id == post_id).all()
    return [_build_react_response(r) for r in reacts]


@router.post("/{match_id}/posts/{post_id}/reacts", response_model=ReactResponse, status_code=201)
def create_react(
    match_id: int,
    post_id: int,
    body: ReactCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """반응 달기."""
    post = db.query(Post).filter(Post.id == post_id, Post.match_id == match_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="인증을 찾을 수 없습니다.")

    react = React(post_id=post_id, user_id=user_id, emoji=body.emoji)
    db.add(react)
    db.commit()
    db.refresh(react)

    return _build_react_response(react)


@router.put("/{match_id}/posts/{post_id}/reacts/{react_id}", response_model=ReactResponse)
def update_react(
    match_id: int,
    post_id: int,
    react_id: int,
    body: ReactUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """반응 수정 (본인 반응만)."""
    react = db.query(React).filter(React.id == react_id, React.post_id == post_id).first()
    if not react:
        raise HTTPException(status_code=404, detail="반응을 찾을 수 없습니다.")
    if react.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인의 반응만 수정할 수 있습니다.")

    react.emoji = body.emoji
    db.commit()
    db.refresh(react)

    return _build_react_response(react)


@router.delete("/{match_id}/posts/{post_id}/reacts/{react_id}", status_code=204)
def delete_react(
    match_id: int,
    post_id: int,
    react_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """반응 삭제 (본인 반응만)."""
    react = db.query(React).filter(React.id == react_id, React.post_id == post_id).first()
    if not react:
        raise HTTPException(status_code=404, detail="반응을 찾을 수 없습니다.")
    if react.user_id != user_id:
        raise HTTPException(status_code=403, detail="본인의 반응만 삭제할 수 있습니다.")

    db.delete(react)
    db.commit()


# ── 내부 헬퍼 ────────────────────────────────────────────

def _build_match_response(match: Match, db: Session) -> MatchResponse:
    participants = []
    for p in match.participants:
        user = p.user
        participants.append(ParticipantResponse(
            user_id=p.user_id,
            username=user.username if user else "unknown",
            joined_at=p.joined_at,
        ))
    return MatchResponse(
        id=match.id,
        mission_id=match.mission_id,
        mission_title=match.mission.title if match.mission else "",
        mission_type=match.mission.type if match.mission else "",
        status=match.status,
        created_at=match.created_at,
        participants=participants,
    )


def _build_post_response(post: Post) -> PostResponse:
    return PostResponse(
        id=post.id,
        match_id=post.match_id,
        user_id=post.user_id,
        username=post.user.username if post.user else "unknown",
        image_url=post.image_url,
        comment=post.comment,
        status=post.status,
        created_at=post.created_at,
    )


def _build_react_response(react: React) -> ReactResponse:
    return ReactResponse(
        id=react.id,
        post_id=react.post_id,
        user_id=react.user_id,
        username=react.user.username if react.user else "unknown",
        emoji=react.emoji,
        created_at=react.created_at,
    )
