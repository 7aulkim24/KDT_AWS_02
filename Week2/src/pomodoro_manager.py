# 포모도로 세션 데이터 클래스 및 관리 매니저

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional
from datetime import datetime


# 포모도로 세션 데이터 클래스
@dataclass
class PomodoroSession:
    id: int
    title: str
    focus_minutes: int
    break_minutes: int
    rounds: int
    status: Literal["pending", "running", "completed"] = "pending"
    
    def __str__(self) -> str:
        return (f"세션 {self.id} [{self.title}] - "
                f"집중 {self.focus_minutes}분 / 휴식 {self.break_minutes}분 "
                f"x {self.rounds}라운드 ({self.status})")


# 포모도로 세션 관리 매니저
class PomodoroManager:
    def __init__(self) -> None:
        self._sessions: Dict[int, PomodoroSession] = {}
        self._next_id: int = 1
        self._running_info: Optional[dict] = None
    
    # 세션 생성
    def create_session(
        self,
        title: str,
        focus_minutes: int,
        break_minutes: int,
        rounds: int
    ) -> PomodoroSession:
        session = PomodoroSession(
            id=self._next_id,
            title=title.strip(),
            focus_minutes=focus_minutes,
            break_minutes=break_minutes,
            rounds=rounds,
            status="pending"
        )
        self._sessions[self._next_id] = session
        self._next_id += 1
        return session
    
    # 세션 조회
    def get_session(self, session_id: int) -> Optional[PomodoroSession]:
        return self._sessions.get(session_id)
    
    # 전체 세션 목록 (ID 순)
    def list_sessions(self) -> List[PomodoroSession]:
        return sorted(self._sessions.values(), key=lambda x: x.id)
    
    # 세션 삭제
    def delete_session(self, session_id: int) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        # 실행 중인 세션은 삭제 불가
        if session.status == "running":
            raise ValueError("실행 중인 세션은 삭제할 수 없습니다.")
        
        del self._sessions[session_id]
        return True
    
    # 세션 상태 업데이트
    def update_session_status(self, session_id: int, status: str) -> bool:
        session = self._sessions.get(session_id)
        if session and status in ["pending", "running", "completed"]:
            session.status = status  # type: ignore
            return True
        return False
    
    # 대기 중 세션 목록
    def get_pending_sessions(self) -> List[PomodoroSession]:
        return [s for s in self._sessions.values() if s.status == "pending"]
    
    # 완료 세션 목록
    def get_completed_sessions(self) -> List[PomodoroSession]:
        return [s for s in self._sessions.values() if s.status == "completed"]
    
    # 세션 개수
    def count_sessions(self) -> int:
        return len(self._sessions)
    
    # 실행 정보 설정
    def set_running_info(self, session_id: int, phase: str, total_seconds: int, current_round: int = 1, total_rounds: int = 1) -> None:
        self._running_info = {
            'session_id': session_id,
            'phase': phase,
            'total_seconds': total_seconds,
            'start_time': datetime.now(),
            'current_round': current_round,
            'total_rounds': total_rounds
        }
    
    # 실행 정보 제거
    def clear_running_info(self) -> None:
        self._running_info = None
    
    # 실행 정보 조회 (메뉴 표시용)
    def get_running_info_string(self) -> Optional[str]:
        if not self._running_info:
            return None
        
        session = self.get_session(self._running_info['session_id'])
        if not session:
            return None
        
        # 경과 시간 계산
        elapsed = (datetime.now() - self._running_info['start_time']).total_seconds()
        elapsed = int(min(elapsed, self._running_info['total_seconds']))
        
        # 소수점 제거하여 정수로 변환
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        total_min = int(self._running_info['total_seconds'] // 60)
        total_sec = int(self._running_info['total_seconds'] % 60)
        
        elapsed_str = f"{elapsed_min:02d}:{elapsed_sec:02d}"
        total_str = f"{total_min:02d}:{total_sec:02d}"
        
        phase_name = "집중" if self._running_info['phase'] == "focus" else "휴식"
        
        # 라운드 정보 추가
        round_info = f"라운드 {self._running_info.get('current_round', 1)}/{self._running_info.get('total_rounds', 1)}"
        
        return f"[실행 중] 세션 {session.id} - {round_info} - {phase_name} | {elapsed_str} / {total_str}"
