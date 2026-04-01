const BASE_URL = 'http://localhost:8000';

// TODO: auth 팀원이 로그인 구현하면 실제 유저 ID로 교체
// 처음 접속 시 유저 ID를 물어보고 localStorage에 저장
function getTempUserId() {
  let id = localStorage.getItem('temp_user_id');
  if (!id) {
    id = prompt('테스트용 유저 ID를 입력하세요 (1~4 중 하나)', '1');
    if (!id) id = '1';
    localStorage.setItem('temp_user_id', id);
  }
  return Number(id);
}

export const CURRENT_USER_ID = getTempUserId();

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-User-Id': CURRENT_USER_ID,
  };
}

export async function getMissions(type = null) {
  const url = type
    ? `${BASE_URL}/missions?type=${encodeURIComponent(type)}`
    : `${BASE_URL}/missions`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('미션 목록을 불러오지 못했습니다.');
  return res.json();
}

export async function createMatch(missionId) {
  const res = await fetch(`${BASE_URL}/matches`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ mission_id: missionId }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || '매칭 요청에 실패했습니다.');
  }
  return res.json();
}

export async function getMatch(matchId) {
  const res = await fetch(`${BASE_URL}/matches/${matchId}`);
  if (!res.ok) throw new Error('매칭 정보를 불러오지 못했습니다.');
  return res.json();
}

export async function getMyActiveMatch() {
  const res = await fetch(`${BASE_URL}/matches/me`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('활성 매치 조회에 실패했습니다.');
  return res.json(); // 없으면 null 반환
}

export async function leaveMatch(matchId) {
  const res = await fetch(`${BASE_URL}/matches/${matchId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('매칭 탈퇴에 실패했습니다.');
}
