# drone_control.py
import time
import logging
import math
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned LocationGlobal has the same altitude as the original location.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except near the poles.
    """
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    return LocationGlobalRelative(newlat, newlon, original_location.alt)

def disable_failsafes(vehicle):
    """GCS 및 스로틀 페일세이프를 비활성화합니다."""
    logging.warning("모든 주요 안전 기능(Failsafe)을 비활성화합니다.")
    vehicle.parameters['FS_GCS_ENABLE'] = 0
    vehicle.parameters['FS_THR_ENABLE'] = 0
    vehicle.parameters['FS_BATT_ENABLE'] = 0
    vehicle.parameters['FS_CRASH_CHECK'] = 0
    vehicle.parameters['FENCE_ENABLE'] = 0
    vehicle.parameters['ARMING_CHECK'] = 0
    logging.info("안전 기능이 비활성화되었습니다.")

def statustext_listener(self, name, message):
    """
    드론으로부터 STATUSTEXT 메시지를 수신하여 로그로 출력합니다.
    특히 Disarm 원인을 파악하는 데 유용합니다.
    """
    logging.warning(f"드론 시스템 메시지: {message.text}")

def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def connect_drone(connection_string):
    """SITL 드론에 연결합니다."""
    logging.info(f"{connection_string}에 연결을 시도합니다...")
    try:
        vehicle = connect(connection_string, wait_ready=True, timeout=60)
        
        # 연결 직후 페일세이프 비활성화
        disable_failsafes(vehicle)

        # Disarm 원인 파악을 위해 상태 메시지 리스너 추가
        vehicle.add_message_listener('STATUSTEXT', statustext_listener)
        logging.info("드론 상태 메시지 리스너를 등록했습니다.")

        logging.info("드론에 성공적으로 연결되었습니다.")
        logging.info(f"드론 정보: {vehicle.version}")
        logging.info(f"현재 모드: {vehicle.mode.name}")
        logging.info(f"무장 상태: {vehicle.armed}")
        return vehicle
    except Exception as e:
        logging.error(f"드론 연결에 실패했습니다: {e}")
        return None

def set_mode(vehicle, mode):
    """드론의 비행 모드를 설정합니다. MAVLink 메시지를 직접 사용합니다."""
    target_mode = VehicleMode(mode.upper())
    current_mode_name = vehicle.mode.name

    if current_mode_name == target_mode.name:
        logging.info(f"이미 {mode.upper()} 모드입니다.")
        return

    logging.info(f"모드를 {mode.upper()}로 변경 명령을 전송합니다...")
    
    # MAV_CMD_DO_SET_MODE 메시지를 생성하여 전송
    # ArduPilot의 모드 번호는 mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED와 함께 사용
    # APM:Copter V3.3용 모드 ID 직접 명시
    _mode_mapping_v3_3 = {
        "STABILIZE": 0,
        "GUIDED": 4,
        "LOITER": 5,
        "RTL": 6,
    }
    mode_id = _mode_mapping_v3_3[mode.upper()]
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        0,       # confirmation
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, # param1: custom mode flag
        mode_id, # param2: custom mode
        0, 0, 0, 0, 0 # params 3-7 (unused)
    )
    vehicle.send_mavlink(msg)

    # 모드가 변경될 때까지 기다립니다 (최대 5초)
    start_time = time.time()
    while vehicle.mode.name != target_mode.name and (time.time() - start_time) < 5:
        logging.info(f"모드 변경 대기 중... 현재 모드: {vehicle.mode.name}")
        time.sleep(0.5)

    if vehicle.mode.name == target_mode.name:
        logging.info(f"모드가 성공적으로 변경되었습니다: {vehicle.mode.name}")
    else:
        logging.error(f"모드 변경 실패: {current_mode_name} -> {target_mode.name}")
        logging.error("드론이 요청된 모드로 변경되지 않았습니다. 비행 명령이 실패할 수 있습니다.")

def arm_drone(vehicle):
    """드론을 무장(arm)합니다."""
    if vehicle.armed:
        logging.info("드론이 이미 무장되어 있습니다.")
        return

    logging.info("드론 무장을 시도합니다...")
    # GUIDED 모드로 먼저 바꾸지 않고, 현재 모드에서 무장을 시도합니다.
    while not vehicle.is_armable:
        logging.info("드론 무장 가능 상태를 대기중입니다...")
        time.sleep(1)

    # 현재 모드가 이륙에 적합하지 않을 수 있으므로, STABILIZE 모드로 설정
    if vehicle.mode.name not in ["STABILIZE", "LOITER"]:
        set_mode(vehicle, "STABILIZE")
        time.sleep(1)

    vehicle.arm(wait=True)

    # 무장 성공 여부 확인
    if not vehicle.armed:
        logging.error("드론 무장에 실패했습니다.")
    else:
        logging.info("드론이 무장되었습니다!")


def takeoff(vehicle, altitude):
    """지정한 고도로 이륙합니다. MAVLink 메시지를 직접 사용합니다."""
    if not vehicle.armed:
        logging.warning("드론이 무장되지 않았습니다. 먼저 무장하세요.")
        return

    logging.info("이륙을 위해 LOITER 모드로 변경합니다...")
    set_mode(vehicle, "LOITER")
    time.sleep(1)

    logging.info(f"이륙 명령 전 현재 모드: {vehicle.mode.name}")
    logging.info(f"{altitude}미터까지 이륙을 시작합니다... (Raw MAVLink command)")
    # MAV_CMD_NAV_TAKEOFF 메시지를 생성하여 전송
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,       # confirmation
        0,       # param 1 (min pitch)
        0,       # param 2 (empty)
        0,       # param 3 (empty)
        0,       # param 4 (yaw)
        0,       # param 5 (lat)
        0,       # param 6 (lon)
        altitude # param 7 (alt)
    )
    vehicle.send_mavlink(msg)

    # 목표 고도에 도달할 때까지 대기
    while True:
        current_altitude = vehicle.location.global_relative_frame.alt
        logging.info(f"현재 고도: {current_altitude:.2f}m")
        if current_altitude >= altitude * 0.95:
            logging.info("목표 고도에 도달했습니다.")
            break
        time.sleep(1)

def go_to(vehicle, lat, lon, alt):
    """지정한 GPS 좌표로 이동합니다."""
    if not vehicle.armed:
        logging.warning("드론이 무장되지 않았습니다.")
        return

    logging.info(f"좌표 ({lat}, {lon}) 고도 {alt}m로 이동합니다.")
    target_location = LocationGlobalRelative(lat, lon, alt)
    vehicle.simple_goto(target_location)

def move_relative(vehicle, heading, distance):
    """지정한 방향과 거리만큼 상대적으로 이동합니다."""
    if not vehicle.armed:
        logging.warning("드론이 무장되지 않았습니다.")
        return

    logging.info(f"방향 {heading}도로 {distance}미터 상대 이동합니다.")
    current_location = vehicle.location.global_relative_frame
    
    # heading(degree)을 radian으로 변환
    heading_rad = math.radians(heading)
    
    # 북쪽, 동쪽 이동 거리 계산
    dNorth = distance * math.cos(heading_rad)
    dEast = distance * math.sin(heading_rad)
    
    # 새로운 GPS 좌표 계산
    target_location = get_location_metres(current_location, dNorth, dEast)
    
    logging.info(f"새로운 목표 지점: {target_location}")
    vehicle.simple_goto(target_location)

    # 목표 지점에 도달할 때까지 대기
    while True:
        distance_to_target = get_distance_metres(vehicle.location.global_relative_frame, target_location)
        logging.info(f"목표 지점까지 남은 거리: {distance_to_target:.2f}m")
        if distance_to_target <= 1:
            logging.info("목표 지점에 도착했습니다.")
            break
        time.sleep(1)

def close_connection(vehicle):
    """드론과의 연결을 종료합니다."""
    if vehicle:
        logging.info("드론과의 연결을 종료합니다.")
        vehicle.close()