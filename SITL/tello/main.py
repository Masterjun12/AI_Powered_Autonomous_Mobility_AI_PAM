# -*- coding: utf-8 -*- 

import logging
from llm_interface import get_drone_command
from command_parser import CommandExecutor
from drone_control import TelloDroneControl

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def main():
    """메인 실행 함수"""
    print("-" * 45)
    print("--- Tello 드론 제어 시뮬레이터 (API-Ready) ---")
    print("자연어 명령을 입력하세요. (예: '앞으로 50cm 이동해')")
    print("프로그램을 종료하려면 'exit'를 입력하세요.")
    print("-" * 45)

    # 1. 핵심 객체들 생성
    drone = TelloDroneControl()
    executor = CommandExecutor(drone)

    try:
        # 드론 SDK 모드 시작
        logging.info("드론 SDK 모드를 시작합니다...")
        executor.execute_command({"command": "command", "parameters": {}})

        while True:
            # 2. 사용자 입력 받기
            try:
                user_input = input("\n명령 입력 > ")
            except EOFError:
                logging.info("입력 스트림이 닫혔습니다. 프로그램을 종료합니다.")
                break

            if user_input.lower() == 'exit':
                logging.info("'exit' 명령을 감지했습니다. 프로그램을 종료합니다.")
                break
            
            if not user_input:
                continue

            # 3. LLM을 통해 명령 변환 (모의 API 호출)
            command_data = get_drone_command(user_input)

            # 4. 변환된 명령 실행
            if command_data:
                executor.execute_command(command_data)

    except KeyboardInterrupt:
        print("\n")
        logging.info("사용자에 의해 프로그램이 중단되었습니다.")
    finally:
        logging.info("시뮬레이터 세션을 종료합니다.")

if __name__ == "__main__":
    main()
