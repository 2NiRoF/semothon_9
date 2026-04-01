from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Mission, Match, MatchParticipant
from schemas import MissionResponse

router = APIRouter(prefix="/missions", tags=["missions"])


def _count_participants(mission: Mission) -> int:
    """현재 참여 중인 인원 수 (waiting/in_progress 매치의 참여자 합산)"""
    total = 0
    for match in mission.matches:
        if match.status in ("waiting", "in_progress"):
            total += len(match.participants)
    return total


@router.get("", response_model=list[MissionResponse])
def get_missions(
    type: Optional[str] = Query(None, description="미션 유형 필터 (예: 플로깅)"),
    db: Session = Depends(get_db),
):
    """미션 목록 조회. ?type=플로깅 처럼 유형 필터 사용 가능."""
    query = db.query(Mission)
    if type:
        query = query.filter(Mission.type == type)
    missions = query.all()

    result = []
    for m in missions:
        result.append(MissionResponse(
            id=m.id,
            title=m.title,
            type=m.type,
            description=m.description,
            max_participants=m.max_participants,
            current_participants=_count_participants(m),
        ))
    return result


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    """특정 미션 상세 조회."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="미션을 찾을 수 없습니다.")

    return MissionResponse(
        id=mission.id,
        title=mission.title,
        type=mission.type,
        description=mission.description,
        max_participants=mission.max_participants,
        current_participants=_count_participants(mission),
    )
