# 비동기 작업 처리 모듈

import asyncio
from pomodoro_manager import PomodoroManager, PomodoroSession

# 타이머 체크 간격 (초)
TIMER_CHECK_INTERVAL = 0.1


# 효율적인 타이머 대기 함수
async def wait_timer(total_seconds: int) -> None:
    # 지정된 시간 동안 대기 (0.1초 단위로 체크)
    loop = asyncio.get_event_loop()
    end_time = loop.time() + total_seconds
    
    while loop.time() < end_time:
        await asyncio.sleep(TIMER_CHECK_INTERVAL)


# 백그라운드 포모도로 실행
async def run_pomodoro_background(
    session: PomodoroSession,
    pomodoro_manager: PomodoroManager
) -> None:
    try:
        pomodoro_manager.update_session_status(session.id, "running")
        
        for round_num in range(1, session.rounds + 1):
            # 집중 시간
            total_seconds = session.focus_minutes * 60
            pomodoro_manager.set_running_info(
                session.id, 
                "focus", 
                total_seconds,
                round_num,
                session.rounds
            )
            
            await wait_timer(total_seconds)
            
            # 휴식 시간 (마지막 라운드 제외)
            if round_num < session.rounds:
                total_seconds = session.break_minutes * 60
                pomodoro_manager.set_running_info(
                    session.id, 
                    "break", 
                    total_seconds,
                    round_num,
                    session.rounds
                )
                
                await wait_timer(total_seconds)
        
        # 완료
        pomodoro_manager.clear_running_info()
        pomodoro_manager.update_session_status(session.id, "completed")
        
    except asyncio.CancelledError:
        pomodoro_manager.clear_running_info()
        pomodoro_manager.update_session_status(session.id, "pending")
        raise
