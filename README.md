# Kanban CLI

터미널에서 프로젝트/백로그를 관리하는 칸반 CLI입니다.

- 프로젝트 생성/선택
- 칸반 보드(TODO / INPROGRESS / REVIEW / DONE) 조회
- 백로그 생성/조회/수정/이동/삭제
- Session 기간 + D-day 표시
- TODO 정렬(생성일 / D-day)

---

## 1) 요구 사항

- Python 3.10+
- `vi` 또는 `vim` (백로그 생성/수정 시 필수)
- `glow` (선택 사항, 상세 보기에서 Markdown 렌더링)

> `glow`가 없으면 상세 보기에서 원문 텍스트로 출력됩니다.

---

## 2) 실행 방법

프로젝트 루트에서 실행:

```bash
python src/main.py
```

혹은 ~/.zshrc에 커스텀 함수를 만들어서 실행:
```bash
echo "kanban() { python \"$(pwd)/src/main.py\" }" >> ~/.zshrc
source ~/.zshrc
```

---

## 3) 데이터 저장 위치

모든 프로젝트 데이터는 아래 경로에 저장됩니다.

```text
~/.kanban/data
```

만약 데이터를 개인 레포로 상태관리하고 싶다면, 
.kanban 이름의 레포 생성하면 된다.
그리고 다른 환경에서 최신화하고 싶으면 ~/ 경로에 clone하면 된다. 

프로젝트를 하나 만들면 대략 아래 구조가 생성됩니다.

```text
~/.kanban/data/<ProjectName>/
  Todo/
  Inprogress/
  Review/
  Done/
```

백로그 파일명 규칙:

```text
001_backlog.md
002_backlog.md
...
```

---

## 4) 화면별 사용법

## 4-1. 프로젝트 목록 화면

- `[N]` 새 프로젝트 생성
- `[Q]` 종료
- `[숫자]` 프로젝트 선택 후 칸반 진입

## 4-2. 칸반 화면

- `[opt]` 옵션 메뉴 진입
- `[sort]` TODO 정렬 기준 변경
- `[B]` 프로젝트 목록으로 복귀

표시 규칙:

- `ID`는 파란색
- `Title`은 볼드
- `Session`은 노란색
- `| D-{day}`는 빨간색 (`D-0`, `D-3`, 지난 일정은 `D+N`)

## 4-3. 옵션(Options) 화면

- `[1] Create Backlog`
- `[2] View Backlog`
- `[3] Edit Backlog`
- `[4] Move Backlog`
- `[5] Delete Backlog`
- `[B]` 칸반으로 복귀

## 4-4. Create Backlog

1. 새 백로그 파일이 `Todo`에 생성됨
2. `vi`가 자동으로 열림
3. `Title`, `Session Start`, `Session End`를 입력 후 저장/종료
4. 검증 성공 시 생성 완료

취소/검증 실패 시 파일이 삭제될 수 있습니다.

## 4-5. View / Edit / Move / Delete 공통

1. 상태 선택 (`0~3`)
2. 백로그 번호 선택
3. 각 동작 실행

리스트에서는 긴 제목이 자동으로 `...` 처리되어 레이아웃이 깨지지 않도록 표시됩니다.

---

## 5) 백로그 Markdown 작성 규칙

파서는 아래 헤더/필드를 기준으로 읽습니다.

필수:

- `# Title` 아래 첫 줄 텍스트
- `# Session` 내부
  - `- Start: YYYY-MM-DD`
  - `- End: YYYY-MM-DD`

예시:

```md
# Title
캡스톤 관련 공부

# What to do
- FastCampus: LLM + RAG

# Why to do
프로젝트 설계 역량 강화

# Session
- Start: 2026-03-29
- End: 2026-04-02

# Note
...
```

검증 규칙:

- Title 비어 있으면 오류
- Start/End 비어 있으면 오류
- 날짜 형식은 `YYYY-MM-DD` 또는 `YYYY/MM/DD` 허용
- End < Start 이면 오류

---

## 6) TODO 정렬 기준

`sort` 명령에서 선택:

- `1` 생성일 순 (오래된 항목 먼저)
- `2` D-day 순 (Session End 임박 순, End 없는 항목은 뒤)

---

## 7) DONE 컬럼 표시 정책

DONE 상태 항목은 최근 7일 기준으로 필터링됩니다.

- End 날짜가 없으면 표시
- End 날짜가 오늘 기준 7일보다 오래되면 숨김

---

## 8) 트러블슈팅

### `vi not found in PATH`

- `vim` 설치 후 재시도
- macOS 예시: `brew install vim`

### `glow` 미설치

- 상세 보기에서 markdown 렌더링 대신 텍스트 출력됨
- 필요 시 설치:
  - macOS: `brew install glow`

### 백로그가 안 보임

- 파일명 규칙이 `*_backlog.md`인지 확인
- `# Title`, `# Session - Start/End` 형식이 맞는지 확인

