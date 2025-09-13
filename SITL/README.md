# LLM 기반 드론 제어 시스템

이 프로젝트는 사용자의 자연어 명령을 해석하여 SITL(Software-in-the-Loop) 시뮬레이션 환경의 드론을 제어하는 시스템입니다.

## 프로젝트 구조

```
SITL/
├─ main.py                  # 진입점, LLM 쿼리 수신 및 전체 흐름 제어
├─ llm_interface.py         # 구글 LLM API 호출 및 자연어 → 명령어 변환 프롬프트 처리
├─ drone_control.py         # Dronekit 기반 드론 제어 함수 모음
├─ command_parser.py        # LLM 응답 파싱 및 기능별 명령으로 변환
├─ config.py                # SITL 접속 정보, LLM API키, 기타 설정
├─ utils.py                 # 공통 유틸 함수 (로깅, 예외처리 등)
├─ requirements.txt         # 필요한 패키지 목록
└─ README.md                # 프로젝트 설명서
```

## 설치 및 설정

1.  **가상환경 생성 및 활성화**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    .\venv\Scripts\activate    # Windows
    ```

2.  **필요한 패키지 설치**

    ```bash
    pip install -r requirements.txt
    ```

3.  **API 키 설정**

    `config.py` 파일을 열고 `GOOGLE_API_KEY` 변수에 자신의 Google Generative AI API 키를 입력합니다.

    ```python
    # config.py
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
    ```

## 실행 방법

1.  **SITL 및 MAVProxy 실행**

    먼저, 드론 시뮬레이터를 실행해야 합니다. Mission Planner를 사용하거나, 터미널에서 직접 `dronekit-sitl`을 실행할 수 있습니다. MAVProxy는 SITL과 통신하여 GCS(Ground Control Station) 역할을 합니다.

    새 터미널을 열고 다음 명령어를 실행하여 SITL을 시작합니다. (예: 서울 시청 근처)

    ```bash
    dronekit-sitl copter --home=37.5665,126.9780,0,180
    ```

    또 다른 터미널을 열고 MAVProxy를 실행하여 SITL에 연결합니다.

    ```bash
    mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
    ```

2.  **메인 스크립트 실행**

    SITL과 MAVProxy가 실행 중인 상태에서, 프로젝트의 메인 스크립트를 실행합니다.

    ```bash
    python main.py
    ```

3.  **명령어 입력**

    스크립트가 실행되면 `명령어 입력 >` 프롬프트가 나타납니다. 여기에 자연어로 명령을 입력하세요.

    **예시 명령어:**

    *   `드론에 연결해`
    *   `가이드 모드로 변경`
    *   `시동 걸어` 또는 `무장해`
    *   `이륙해서 15미터로 올라가`
    *   `연결 종료`
    *   `exit` (프로그램 종료)
