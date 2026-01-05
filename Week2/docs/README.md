# 포모도로 타이머 CLI 프로그램 (과제 2)

## 프로젝트 개요

백그라운드 실행과 실시간 화면 갱신이 가능한 포모도로 타이머 CLI 프로그램입니다. Python 응용 기능(비동기, 제너레이터, 타입 힌트 등)을 활용하여 구현했습니다.

## 파일 구조

```
Week2/
├── main.py              # 메인 실행 + 메뉴 UI
├── models.py            # 데이터 클래스 (PomodoroSession)
├── pomodoro_manager.py  # 세션 관리 및 상태 추적
├── async_tasks.py       # 비동기 백그라운드 실행
└── utils.py             # 유틸리티 (제너레이터, 입력 검증)
```

## 주요 기능

### 포모도로 세션 관리
- **세션 생성**: 제목, 집중/휴식 시간, 라운드 수 설정
- **백그라운드 실행**: 메뉴를 사용하면서 동시에 타이머 실행
- **실시간 화면 자동 갱신**: 1초마다 화면이 자동으로 업데이트되어 진행 상황 표시
- **세션 목록 조회**: 전체 세션 및 상태별 통계 (pending, running, completed)
- **세션 삭제**: 완료되거나 대기 중인 세션 삭제 (실행 중 삭제 불가)

### 메뉴 구조

```
==================================================
포모도로 타이머
==================================================
1. 포모도로 세션 생성
2. 포모도로 실행
3. 세션 목록 조회
4. 포모도로 세션 삭제
0. 프로그램 종료
==================================================
```

## Python 고급 기능 활용

### 1. 비동기 처리 (asyncio)

**백그라운드 포모도로 실행**

```python
async def run_pomodoro_background(
    session: PomodoroSession,
    pomodoro_manager: PomodoroManager
) -> None:
    try:
        pomodoro_manager.update_session_status(session.id, "running")
        
        for round_num in range(1, session.rounds + 1):
            # 집중 시간
            total_seconds = session.focus_minutes * 60
            pomodoro_manager.set_running_info(session.id, "focus", total_seconds)
            
            for _ in range(total_seconds):
                await asyncio.sleep(1)
            
            # 휴식 시간 (마지막 라운드 제외)
            if round_num < session.rounds:
                total_seconds = session.break_minutes * 60
                pomodoro_manager.set_running_info(session.id, "break", total_seconds)
                
                for _ in range(total_seconds):
                    await asyncio.sleep(1)
        
        pomodoro_manager.clear_running_info()
        pomodoro_manager.update_session_status(session.id, "completed")
        
    except asyncio.CancelledError:
        pomodoro_manager.clear_running_info()
        pomodoro_manager.update_session_status(session.id, "pending")
        raise
```

**실시간 화면 자동 갱신**

```python
async def screen_refresher() -> None:
    last_info = None
    while True:
        await asyncio.sleep(1)  # 1초마다 확인
        
        running_info = pomodoro_manager.get_running_info_string()
        
        # 상태가 변경되었을 때만 화면 갱신
        if running_info != last_info and running_info is not None:
            show_menu()
            print("\n메뉴 선택 (0-4): ", end="", flush=True)
            last_info = running_info
```

**비동기 입력 처리**

```python
async def ainput(prompt: str = "") -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(input, prompt))
```

### 2. 제너레이터 (Generator)

메모리 효율적인 데이터 생성

```python
def session_list_generator(sessions: List[PomodoroSession]) -> Iterator[str]:
    if not sessions:
        yield "생성된 세션이 없습니다."
        return
    
    yield from (str(session) for session in sessions)
    yield f"\n총 {len(sessions)}개의 세션"
```

### 3. 타입 힌트 (Type Hints)

모든 함수에 타입 명시

```python
def create_session(
    self,
    title: str,
    focus_minutes: int,
    break_minutes: int,
    rounds: int
) -> PomodoroSession:
    ...
```

### 4. 예외 처리

안전한 입력 검증

```python
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
```

### 5. List Comprehension

간결한 데이터 필터링

```python
def get_pending_sessions(self) -> List[PomodoroSession]:
    return [s for s in self._sessions.values() if s.status == "pending"]

def get_completed_sessions(self) -> List[PomodoroSession]:
    return [s for s in self._sessions.values() if s.status == "completed"]
```

### 6. 데이터 클래스 (dataclass)

```python
@dataclass
class PomodoroSession:
    id: int
    title: str
    focus_minutes: int
    break_minutes: int
    rounds: int
    status: Literal["pending", "running", "completed"] = "pending"
```

## 실행 방법

```bash
cd Week2
python main.py
```

## 실행 예시

### 1. 세션 생성
```
포모도로 세션 생성
--------------------------------------------------
세션 제목: 알고리즘 공부
집중 시간 (분): 25
휴식 시간 (분): 5
라운드 수: 4

세션이 생성되었습니다.
   세션 1 [알고리즘 공부] - 집중 25분 / 휴식 5분 x 4라운드 (pending)
```

### 2. 세션 실행 및 실시간 모니터링
```
==================================================
포모도로 타이머
==================================================

[실행 중] 세션 1 - 집중 | 12:34 / 25:00
--------------------------------------------------

1. 포모도로 세션 생성
2. 포모도로 실행
3. 세션 목록 조회
4. 포모도로 세션 삭제
0. 프로그램 종료
==================================================

메뉴 선택 (0-4): 
```
※ 화면이 1초마다 자동으로 갱신되어 진행 시간이 업데이트됩니다.

### 3. 세션 목록 조회
```
세션 목록
==================================================
세션 1 [알고리즘 공부] - 집중 25분 / 휴식 5분 x 4라운드 (running)
세션 2 [영어 공부] - 집중 30분 / 휴식 10분 x 2라운드 (pending)
세션 3 [독서] - 집중 50분 / 휴식 10분 x 1라운드 (completed)

총 3개의 세션

상태별 통계: 대기 1개 | 완료 1개
```

## 주요 특징

### 백그라운드 실행
- 포모도로 타이머가 백그라운드에서 실행되어 메뉴 사용 가능
- `asyncio.create_task()`로 독립적인 태스크 생성

### 실시간 화면 갱신
- 1초마다 자동으로 화면 업데이트
- 실행 중인 세션의 경과 시간 실시간 표시
- 깔끔한 화면 관리 (`clear_screen()`)

### 비동기 입력 처리
- 입력 대기 중에도 백그라운드 태스크 실행 가능
- `loop.run_in_executor()`를 사용한 논블로킹 입력

### 안전한 상태 관리
- 실행 중인 세션은 삭제 불가
- 취소 시 자동으로 pending 상태로 복원
- 프로그램 종료 시 실행 중인 태스크 정리

## 기술 스택

| 항목 | 내용 |
|------|------|
| **Python 버전** | 3.10+ |
| **비동기 처리** | asyncio |
| **데이터 모델** | dataclass, typing |
| **파일 수** | 5개 |

## 파일별 역할

| 파일 | 역할 | 주요 기능 |
|------|------|-----------|
| `main.py` | 메인 실행 및 UI | 메뉴, 화면 갱신, 비동기 입력 |
| `models.py` | 데이터 모델 | PomodoroSession 클래스 |
| `pomodoro_manager.py` | 세션 관리 | CRUD, 상태 관리, 실행 정보 추적 |
| `async_tasks.py` | 비동기 작업 | 백그라운드 포모도로 실행 |
| `utils.py` | 유틸리티 | 입력 검증, 제너레이터 |
