# command_parser.py
import json
import logging
import drone_control
import config

def parse_and_execute_commands(vehicle, llm_response: str):
    """
    LLM의 JSON 배열 응답을 파싱하여 포함된 모든 명령을 순차적으로 실행합니다.
    vehicle 객체 상태를 관리하고 반환합니다.
    """
    try:
        if not llm_response:
            logging.warning("LLM으로부터 빈 응답을 받았습니다.")
            return vehicle

        command_list = json.loads(llm_response)

        # LLM이 단일 객체를 반환한 경우, 리스트로 감싸서 처리
        if not isinstance(command_list, list):
            command_list = [command_list]

        for command_data in command_list:
            command = command_data.get("command")
            params = command_data.get("parameters", {})

            logging.info(f"수신된 명령: {command}, 파라미터: {params}")

            if command == "connect":
                if vehicle:
                    drone_control.close_connection(vehicle)
                vehicle = drone_control.connect_drone(config.CONNECTION_STRING)
                if not vehicle: # 연결 실패 시 즉시 중단
                    logging.error("연결에 실패하여 이후 명령을 중단합니다.")
                    return None
                continue # 다음 명령으로
            
            # 'connect' 외의 모든 명령은 vehicle 객체가 필요합니다.
            if not vehicle:
                logging.error("드론이 연결되지 않았습니다. 먼저 'connect' 명령을 실행하세요.")
                return None # 이후 명령을 모두 중단

            if command == "set_mode":
                if "mode" in params:
                    drone_control.set_mode(vehicle, params["mode"])
                else:
                    logging.error("'set_mode' 명령에 'mode' 파라미터가 필요합니다.")

            elif command == "arm":
                drone_control.arm_drone(vehicle)

            elif command == "takeoff":
                if "altitude" in params:
                    drone_control.takeoff(vehicle, params["altitude"])
                else:
                    logging.error("'takeoff' 명령에 'altitude' 파라미터가 필요합니다.")

            elif command == "move_relative":
                if all(k in params for k in ["heading", "distance"]):
                    drone_control.move_relative(vehicle, params["heading"], params["distance"])
                else:
                    logging.error("'move_relative' 명령에 'heading', 'distance' 파라미터가 필요합니다.")

            elif command == "close":
                drone_control.close_connection(vehicle)
                vehicle = None # 연결이 종료되었으므로 None으로 설정
                logging.info("연결이 종료되었습니다. 이후 명령을 중단합니다.")
                return None # 즉시 함수 종료

            else:
                logging.warning(f"알 수 없는 명령입니다: {command}")

    except json.JSONDecodeError:
        logging.error(f"잘못된 JSON 형식의 응답입니다: {llm_response}")
    except Exception as e:
        logging.error(f"명령 실행 중 오류 발생: {e}")

    return vehicle # 현재 vehicle 상태 반환