# main.py
import logging
from utils import setup_logging
import llm_interface
import command_parser

def main():
    """메인 실행 함수"""
    setup_logging()
    logging.info("LLM 기반 드론 제어 시스템을 시작합니다.")
    logging.info("명령 예시: '드론 연결', '10미터 이륙', '가이드 모드'")
    logging.info("종료하려면 'exit'을 입력하세요.")

    vehicle = None

    while True:
        try:
            #query = input("명령어 입력 > ")
            query = "연결, 시동, 이륙, 고도 50미터, 대각선 200미터 이동, 착륙, 시동 꺼"

            if query.lower() == 'exit':
                if vehicle:
                    command_parser.parse_and_execute(vehicle, '{"command": "close"}')
                logging.info("시스템을 종료합니다.")
                break

            if not query:
                continue

            # LLM을 통해 자연어 명령을 JSON으로 변환
            llm_response = llm_interface.get_drone_command(query)

            # JSON 명령을 파싱하고 실행
            vehicle = command_parser.parse_and_execute_commands(vehicle, llm_response)

        except KeyboardInterrupt:
            if vehicle:
                command_parser.parse_and_execute(vehicle, '{"command": "close"}')
            logging.info("\n사용자에 의해 종료되었습니다.")
            break
        except Exception as e:
            logging.error(f"메인 루프에서 예기치 않은 오류 발생: {e}")

if __name__ == "__main__":
    main()
