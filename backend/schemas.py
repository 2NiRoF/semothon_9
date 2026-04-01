from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# ── User (간단히 참조용) ──────────────────────────────
class UserBrief(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# ── Mission ──────────────────────────────────────────
class MissionResponse(BaseModel):
    id: int
    title: str
    type: str
    description: Optional[str]
    max_participants: int
    current_participants: int  # 계산 필드

    class Config:
        from_attributes = True


# ── Match ────────────────────────────────────────────
class MatchCreate(BaseModel):
    mission_id: int


class ParticipantResponse(BaseModel):
    user_id: int
    username: str
    joined_at: datetime

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    mission_id: int
    mission_title: str
    mission_type: str
    status: str
    created_at: datetime
    participants: list[ParticipantResponse]

    class Config:
        from_attributes = True


# ── Post ─────────────────────────────────────────────
class PostResponse(BaseModel):
    id: int
    match_id: int
    user_id: int
    username: str
    image_url: Optional[str]
    comment: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── React ────────────────────────────────────────────
class ReactCreate(BaseModel):
    emoji: str


class ReactUpdate(BaseModel):
    emoji: str


class ReactResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    username: str
    emoji: str
    created_at: datetime

    class Config:
        from_attributes = True
