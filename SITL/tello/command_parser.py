# -*- coding: utf-8 -*-

"""
이 파일은 LLM으로부터 받은 구조화된 명령을 실제 드론 제어 함수에 연결하고 실행하는 역할을 합니다.
파일 이름은 command_parser이지만, 실제 클래스 이름은 CommandExecutor로 하여 역할을 명확히 합니다.
"""

from drone_control import TelloDroneControl

class CommandExecutor:
    """
    LLM이 생성한 명령 딕셔너리를 받아, 해당하는 TelloDroneControl의 메소드를 실행합니다.
    """
    def __init__(self, drone_control: TelloDroneControl):
        """
        CommandExecutor를 초기화합니다.

        Args:
            drone_control (TelloDroneControl): 실제 드론 제어 함수를 담고 있는 객체.
        """
        self.drone = drone_control
        # 명령어 문자열과 실제 실행될 함수를 매핑하는 딕셔너리입니다.
        # 이 방식을 사용하면 eval() 없이 안전하게 함수를 호출할 수 있습니다.
        self.command_map = {
            # 제어 명령
            "command": self.drone.command,
            "takeoff": self.drone.takeoff,
            "land": self.drone.land,
            "emergency": self.drone.emergency,
            "up": self.drone.up,
            "down": self.drone.down,
            "left": self.drone.left,
            "right": self.drone.right,
            "forward": self.drone.forward,
            "back": self.drone.back,
            "cw": self.drone.cw,
            "ccw": self.drone.ccw,
            "flip": self.drone.flip,
            # 상태 조회 명령
            "get_speed": self.drone.get_speed,
            "get_battery": self.drone.get_battery,
            "get_time": self.drone.get_time,
            "get_wifi_snr": self.drone.get_wifi_snr,
            # 스트림 명령
            "streamon": self.drone.streamon,
            "streamoff": self.drone.streamoff,
        }
        print("[INFO] CommandExecutor 객체가 생성되었습니다.")

    def execute_command(self, command_data: dict):
        """
        전달받은 딕셔너리로부터 명령을 찾아 실행합니다.

        Args:
            command_data (dict): {"command": str, "parameters": dict} 형태의 딕셔너리.
        """
        command_name = command_data.get("command")
        parameters = command_data.get("parameters", {})

        if not command_name:
            print("[ERROR] 명령 딕셔너리에 'command' 키가 없습니다.")
            return

        # 'error' 명령은 LLM이 명령을 이해하지 못했을 때 생성하는 특별한 경우입니다.
        if command_name == "error":
            reason = parameters.get("reason", "알 수 없는 이유")
            print(f"[LLM_ERROR] LLM이 명령을 처리하지 못했습니다: {reason}")
            return

        # command_map에서 실행할 함수를 찾습니다.
        func_to_execute = self.command_map.get(command_name)

        if func_to_execute:
            try:
                # 파라미터를 함께 넣어 함수를 실행합니다 (e.g., drone.forward(x=50))
                func_to_execute(**parameters)
            except TypeError as e:
                # 함수에 잘못된 파라미터가 전달된 경우
                print(f"[ERROR] '{command_name}' 명령 실행 중 오류: 잘못된 파라미터입니다. {e}")
            except Exception as e:
                # 기타 예외 처리
                print(f"[ERROR] '{command_name}' 명령 실행 중 예기치 않은 오류 발생: {e}")
        else:
            # command_map에 존재하지 않는 명령인 경우
            print(f"[ERROR] 알 수 없는 명령입니다: '{command_name}'. 프롬프트와 command_map을 확인하세요.")