# 포모도로 타이머 CLI 프로그램 (화면 자동 갱신)

import asyncio
import os
from typing import NoReturn, Optional
from functools import partial
from pomodoro_manager import PomodoroManager, PomodoroSession
from utils import (
    safe_int_input,
    safe_string_input,
    session_list_generator,
    print_header,
    print_separator,
    print_section,
    wait_for_enter
)
from async_tasks import run_pomodoro_background

pomodoro_manager = PomodoroManager()

# 현재 실행 중인 백그라운드 태스크
current_task: Optional[asyncio.Task] = None

# 비동기 입력 함수
async def ainput(prompt: str = "") -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(input, prompt))

# 화면 클리어
def clear_screen() -> None:
    os.system('clear' if os.name != 'nt' else 'cls')


# 메인 메뉴 출력
def show_menu() -> None:
    clear_screen()
    
    print_header("포모도로 타이머")
    
    # 실행 중인 세션 정보 표시
    running_info = pomodoro_manager.get_running_info_string()
    if running_info:
        print(f"\n{running_info}")
        print_separator()
    
    print("\n1. 포모도로 세션 생성")
    print("2. 포모도로 실행")
    print("3. 세션 목록 조회")
    print("4. 포모도로 세션 삭제")
    print("0. 프로그램 종료")
    print_separator("=")


# 실시간 화면 갱신
async def screen_refresher() -> None:
    last_info = None
    while True:
        await asyncio.sleep(1)  # 1초마다 확인
        running_info = pomodoro_manager.get_running_info_string()
        
        # 상태가 변경되었을 때 화면 갱신
        if running_info != last_info:
            show_menu()
            print("\n메뉴 선택 (0-4): ", end="", flush=True)
            last_info = running_info


# 포모도로 세션 생성 처리
def handle_create_session() -> None:
    try:
        print_section("포모도로 세션 생성")
        
        title = safe_string_input("세션 제목: ")
        focus_minutes = safe_int_input("집중 시간 (분): ", min_value=1)
        break_minutes = safe_int_input("휴식 시간 (분): ", min_value=1)
        rounds = safe_int_input("라운드 수: ", min_value=1)
        
        session = pomodoro_manager.create_session(
            title, focus_minutes, break_minutes, rounds
        )
        
        print(f"\n세션이 생성되었습니다.")
        print(f"   {session}")
        wait_for_enter()
        
    except ValueError as e:
        print(f"\n오류: {e}")
        wait_for_enter()
    except KeyboardInterrupt:
        print("\n세션 생성이 취소되었습니다.")


# 포모도로 세션 백그라운드 실행
async def handle_run_session() -> None:
    global current_task
    
    try:
        print_section("포모도로 실행")
        
        if current_task and not current_task.done():
            print("이미 실행 중인 세션이 있습니다.")
            wait_for_enter()
            return
        
        pending_sessions = pomodoro_manager.get_pending_sessions()
        if not pending_sessions:
            print("실행 가능한 세션이 없습니다. 먼저 세션을 생성해주세요.")
            wait_for_enter()
            return
        
        print("실행 가능한 세션:")
        for session in pending_sessions:
            print(f"  {session}")
        print()
        
        session_id = safe_int_input("실행할 세션 ID: ", min_value=1)
        
        session = pomodoro_manager.get_session(session_id)
        if not session:
            print(f"\nID {session_id}번 세션을 찾을 수 없습니다.")
            wait_for_enter()
            return
        
        if session.status != "pending":
            print(f"\n이 세션은 이미 {session.status} 상태입니다.")
            wait_for_enter()
            return
        
        current_task = asyncio.create_task(
            run_pomodoro_background(session, pomodoro_manager)
        )
        
        await asyncio.sleep(0.1)
        
        print(f"\n세션 {session_id}이(가) 백그라운드에서 시작되었습니다.")
        print("화면이 자동으로 업데이트됩니다.")
        wait_for_enter()
        
    except ValueError as e:
        print(f"\n오류: {e}")
        wait_for_enter()
    except KeyboardInterrupt:
        print("\n실행이 취소되었습니다.")


# 세션 목록 조회 처리
def handle_list_sessions() -> None:
    print_section("세션 목록")
    print_separator("=")
    
    sessions = pomodoro_manager.list_sessions()
    for line in session_list_generator(sessions):
        print(line)
    
    if sessions:
        pending = len(pomodoro_manager.get_pending_sessions())
        completed = len(pomodoro_manager.get_completed_sessions())
        print(f"\n상태별 통계: 대기 {pending}개 | 완료 {completed}개")
    
    wait_for_enter()


# 포모도로 세션 삭제 처리
async def handle_delete_session() -> None:
    try:
        print_section("포모도로 세션 삭제")
        
        if pomodoro_manager.count_sessions() == 0:
            print("등록된 세션이 없습니다.")
            wait_for_enter()
            return
        
        print("현재 세션 목록:")
        for session in pomodoro_manager.list_sessions():
            print(f"  {session}")
        print()
        
        session_id = safe_int_input("삭제할 세션 ID: ", min_value=1)
        
        session = pomodoro_manager.get_session(session_id)
        if not session:
            print(f"\nID {session_id}번 세션을 찾을 수 없습니다.")
            wait_for_enter()
            return
        
        confirm = (await ainput(f"'{session.title}' 세션을 삭제하시겠습니까? (y/n): ")).strip().lower()
        if confirm != 'y':
            print("삭제가 취소되었습니다.")
        elif pomodoro_manager.delete_session(session_id):
            print(f"\n'{session.title}' 세션이 삭제되었습니다.")
        else:
            print(f"\n세션 삭제에 실패했습니다.")
        
        wait_for_enter()
            
    except ValueError as e:
        print(f"\n오류: {e}")
        wait_for_enter()
    except KeyboardInterrupt:
        print("\n세션 삭제가 취소되었습니다.")


# 메인 메뉴 루프 (비동기)
async def main_menu() -> NoReturn:
    global current_task
    
    clear_screen()
    print("\n" + "=" * 50)
    print("포모도로 타이머에 오신 것을 환영합니다.")
    print_separator("=")
    input("\nEnter를 눌러 시작...")
    
    # 화면 갱신 태스크 시작
    refresh_task = asyncio.create_task(screen_refresher())
    
    try:
        while True:
            try:
                show_menu()
                choice = (await ainput("\n메뉴 선택 (0-4): ")).strip()
                
                if choice == "1":
                    handle_create_session()
                elif choice == "2":
                    await handle_run_session()
                elif choice == "3":
                    handle_list_sessions()
                elif choice == "4":
                    await handle_delete_session()
                elif choice == "0":
                    if current_task and not current_task.done():
                        current_task.cancel()
                        try:
                            await current_task
                        except asyncio.CancelledError:
                            pass
                    
                    clear_screen()
                    print("\n" + "=" * 50)
                    print("프로그램을 종료합니다.")
                    print_separator("=")
                    print()
                    break
                else:
                    print("\n잘못된 입력입니다. 0-4 사이의 숫자를 입력해주세요.")
                    wait_for_enter()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n예상치 못한 오류: {e}")
                wait_for_enter()
    finally:
        refresh_task.cancel()
        try:
            await refresh_task
        except asyncio.CancelledError:
            pass


# 프로그램 진입점
def main() -> None:
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\n\n프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n치명적인 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
