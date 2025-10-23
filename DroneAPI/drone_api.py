import time
import re

class DroneTimeBasedAPI:
    """
    LLM이 생성한 각 명령어(command)를 받아,
    동작을 시뮬레이션하고 예상 시간만큼 대기하는 API.
    """
    # 드론의 성능 스펙 (cm/s, deg/s)
    DEFAULT_SPEED = 30.0  # 30 cm/s (상승 및 수평 이동 속도)
    ROTATION_SPEED = 90.0 # 90 deg/s

    def __init__(self):
        print("✅ [API] 드론 시뮬레이션 API가 초기화되었습니다.")
        self.current_speed = self.DEFAULT_SPEED

    def _wait_for_distance(self, distance):
        wait_time = abs(float(distance)) / self.current_speed
        print(f"  ... [API] 예상 소요 시간: {wait_time:.2f}초. 대기를 시작합니다.")
        time.sleep(wait_time)

    def _wait_for_degree(self, degree):
        wait_time = abs(float(degree)) / self.ROTATION_SPEED
        print(f"  ... [API] 예상 소요 시간: {wait_time:.2f}초. 대기를 시작합니다.")
        time.sleep(wait_time)

    def takeoff(self, altitude: int = 50, **kwargs):
        """
        주어진 고도까지 이륙합니다. 고도가 없으면 기본 50cm로 이륙합니다.
        """
        print(f"🚀 [API] 'takeoff' 액션 실행. 목표 고도: {altitude}cm")
        self._wait_for_distance(altitude) # 고도까지 올라가는 시간 계산
        print("✅ [API] 'takeoff' 액션 완료.")

    def land(self, **kwargs):
        print("🛬 [API] 'land' 액션 실행.")
        time.sleep(3) # 착륙은 3초 정도로 가정
        print("✅ [API] 'land' 액션 완료.")

    def up(self, distance: int, **kwargs):
        print(f"⬆️  [API] 'up' 액션 실행. 거리: {distance}cm")
        self._wait_for_distance(distance)
        print(f"✅ [API] 'up' 액션 완료.")

    def down(self, distance: int, **kwargs):
        print(f"⬇️  [API] 'down' 액션 실행. 거리: {distance}cm")
        self._wait_for_distance(distance)
        print(f"✅ [API] 'down' 액션 완료.")

    def left(self, distance: int, **kwargs):
        print(f"⬅️  [API] 'left' 액션 실행. 거리: {distance}cm")
        self._wait_for_distance(distance)
        print(f"✅ [API] 'left' 액션 완료.")

    def right(self, distance: int, **kwargs):
        print(f"➡️  [API] 'right' 액션 실행. 거리: {distance}cm")
        self._wait_for_distance(distance)
        print(f"✅ [API] 'right' 액션 완료.")

    def forward(self, distance: int, **kwargs):
        print(f"⤴️  [API] 'forward' 액션 실행. 거리: {distance}cm")
        self._wait_for_distance(distance)
        print(f"✅ [API] 'forward' 액션 완료.")

    def back(self, distance: int, **kwargs):
        print(f"⤵️  [API] 'back' 액션 실행. 거리: {distance}cm")
        self._wait_for_distance(distance)
        print(f"✅ [API] 'back' 액션 완료.")

    def cw(self, degree: int, **kwargs):
        print(f"↪️  [API] 'cw' (시계방향 회전) 액션 실행. 각도: {degree}°")
        self._wait_for_degree(degree)
        print(f"✅ [API] 'cw' 액션 완료.")

    def ccw(self, degree: int, **kwargs):
        print(f"↩️  [API] 'ccw' (반시계방향 회전) 액션 실행. 각도: {degree}°")
        self._wait_for_degree(degree)
        print(f"✅ [API] 'ccw' 액션 완료.")

    def go(self, x: int, y: int, z: int, speed: int, **kwargs):
        print(f"↗️  [API] 'go' 액션 실행. 목표:({x},{y},{z}), 속도:{speed}cm/s")
        distance = (float(x)**2 + float(y)**2 + float(z)**2)**0.5
        wait_time = distance / float(speed)
        print(f"  ... [API] 예상 소요 시간: {wait_time:.2f}초. 대기를 시작합니다.")
        time.sleep(wait_time)
        print(f"✅ [API] 'go' 액션 완료.")

    def speed(self, value: int, **kwargs):
        print(f"💨 [API] 'speed' 변경. 새로운 속도: {value} cm/s")
        self.current_speed = float(value)
        time.sleep(0.1) # 속도 변경은 즉시 적용된다고 가정
        print(f"✅ [API] 'speed' 액션 완료.")

    def emergency(self, **kwargs):
        print("🚨 [API] 'emergency' 액션 실행.")
        time.sleep(1)
        print("✅ [API] 'emergency' 액션 완료.")

    def __getattr__(self, name):
        def method(**kwargs):
            print(f"ℹ️  [API] '{name}' 액션 실행. 파라미터: {kwargs}")
            time.sleep(0.5) # 간단한 설정은 0.5초로 가정
            print(f"✅ [API] '{name}' 액션 완료.")
        return method

