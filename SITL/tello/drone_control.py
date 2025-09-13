# -*- coding: utf-8 -*-

"""
이 파일은 Tello 드론의 실제 제어 명령을 담당하는 함수들을 정의합니다.
각 함수는 Tello SDK에 명시된 특정 명령에 해당합니다.
본 시뮬레이션 환경에서는 실제 드론에 명령을 보내는 대신,
어떤 명령이 실행되었는지 콘솔에 출력하는 방식으로 동작을 "시뮬레이션"합니다.
"""

class TelloDroneControl:
    """
    Tello 드론을 제어하는 명령을 포함하는 클래스입니다.
    """
    def __init__(self):
        # 실제 드론과 연결되었다고 가정하는 상태 변수
        self.is_connected = False
        print("[INFO] TelloDroneControl 객체가 생성되었습니다.")

    def _execute_command(self, command_name, **kwargs):
        """
        명령 실행을 시뮬레이션하고 결과를 출력하는 내부 함수.
        실제 드론 연결 시, 이 부분에 소켓 통신 코드가 들어갑니다.
        """
        # 'command' 명령 외에는 드론과 연결되어 있어야 실행 가능
        if not self.is_connected and command_name != "command":
            print(f"[ERROR] 드론이 연결되지 않았습니다. '{command_name}' 명령을 실행할 수 없습니다.")
            return "error"
            
        param_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        print(f"[ACTION] >> {command_name} | 파라미터: {param_str if param_str else '없음'}")
        return "ok"

    # --- 상태 조회 명령 (Read Commands) ---
    def get_speed(self):
        return self._execute_command("speed?")

    def get_battery(self):
        return self._execute_command("battery?")

    def get_time(self):
        return self._execute_command("time?")

    def get_wifi_snr(self):
        return self._execute_command("wifi?")

    # --- 제어 명령 (Control Commands) ---
    def command(self):
        """SDK 모드로 진입합니다."""
        self.is_connected = True
        return self._execute_command("command")

    def takeoff(self):
        """자동으로 이륙합니다."""
        return self._execute_command("takeoff")

    def land(self):
        """자동으로 착륙합니다."""
        return self._execute_command("land")

    def streamon(self):
        """비디오 스트림을 켭니다."""
        return self._execute_command("streamon")

    def streamoff(self):
        """비디오 스트림을 끕니다."""
        return self._execute_command("streamoff")

    def emergency(self):
        """모든 모터를 즉시 정지합니다."""
        return self._execute_command("emergency")

    def up(self, x: int):
        """x cm 만큼 위로 올라갑니다. (x: 20-500)"""
        return self._execute_command("up", x=x)

    def down(self, x: int):
        """x cm 만큼 아래로 내려갑니다. (x: 20-500)"""
        return self._execute_command("down", x=x)

    def left(self, x: int):
        """x cm 만큼 왼쪽으로 이동합니다. (x: 20-500)"""
        return self._execute_command("left", x=x)

    def right(self, x: int):
        """x cm 만큼 오른쪽으로 이동합니다. (x: 20-500)"""
        return self._execute_command("right", x=x)

    def forward(self, x: int):
        """x cm 만큼 앞으로 이동합니다. (x: 20-500)"""
        return self._execute_command("forward", x=x)

    def back(self, x: int):
        """x cm 만큼 뒤로 이동합니다. (x: 20-500)"""
        return self._execute_command("back", x=x)

    def cw(self, x: int):
        """시계 방향으로 x 도 회전합니다. (x: 1-360)"""
        return self._execute_command("cw", x=x)

    def ccw(self, x: int):
        """반시계 방향으로 x 도 회전합니다. (x: 1-360)"""
        return self._execute_command("ccw", x=x)

    def flip(self, direction: str):
        """지정된 방향으로 플립합니다. (l, r, f, b)"""
        return self._execute_command("flip", direction=direction)