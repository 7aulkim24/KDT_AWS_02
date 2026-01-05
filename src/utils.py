# 유틸리티 함수: 제너레이터 및 입력 검증

from typing import Iterator, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pomodoro_manager import PomodoroSession


# Enter 입력 대기
def wait_for_enter(message: str = "\nEnter를 눌러 계속...") -> None:
    input(message)


# 정수 입력 검증
def safe_int_input(prompt: str, min_value: int = 1) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < min_value:
                print(f"{min_value} 이상의 숫자를 입력해주세요.")
                continue
            return value
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n입력이 취소되었습니다.")
            raise


# 문자열 입력 검증
def safe_string_input(prompt: str) -> str:
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("빈 값은 입력할 수 없습니다.")
                continue
            return value
        except KeyboardInterrupt:
            print("\n입력이 취소되었습니다.")
            raise


# 헤더 출력
def print_header(title: str, width: int = 50) -> None:
    print("=" * width)
    print(title)
    print("=" * width)

# 구분선 출력
def print_separator(char: str = "-", width: int = 50) -> None:
    print(char * width)


# 섹션 헤더 출력
def print_section(title: str, width: int = 50) -> None:
    print(f"\n{title}")
    print("-" * width)


# 세션 목록 생성
def session_list_generator(sessions: List[PomodoroSession]) -> Iterator[str]:
    if not sessions:
        yield "생성된 세션이 없습니다."
        return
    
    yield from (str(session) for session in sessions)
    yield f"\n총 {len(sessions)}개의 세션"
