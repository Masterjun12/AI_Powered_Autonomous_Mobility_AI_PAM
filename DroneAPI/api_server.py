from flask import Flask, request, jsonify
from mission_executor import MissionExecutor
from drone_api import DroneTimeBasedAPI
import threading
import json
import traceback

app = Flask(__name__)

# --- 전역 객체 초기화 ---
drone_api = DroneTimeBasedAPI()
executor = MissionExecutor(drone_api)
# -------------------------

def run_mission_background(task: str):
    """
    미리 생성된 JSON 파일을 읽어 미션을 수행하는 함수.
    VLLM 호출 로직이 제거되었습니다.
    """
    print(f"\n--- [Thread] 수신된 작업: '{task}'. 파일에서 미션 계획을 읽습니다. ---")

    mission_file = "sample_mission.json"

    try:
        # 1. 미리 생성된 미션 계획 JSON 파일을 읽습니다.
        print(f"--- [Thread] '{mission_file}' 파일에서 미션 계획을 읽는 중... ---")
        with open(mission_file, 'r', encoding='utf-8') as f:
            mission_plan = json.load(f)
        
        print("--- [Thread] 미션 계획 로딩 성공! 실행기로 전달합니다. ---")
        
        # 2. 불러온 계획을 실행기에게 전달하여 미션을 수행합니다.
        executor.execute_mission(mission_plan)

    except FileNotFoundError:
        print(f"❌ [Thread-Error] 미션 파일을 찾을 수 없습니다: '{mission_file}'")
    except json.JSONDecodeError:
        print(f"❌ [Thread-Error] '{mission_file}' 파일의 JSON 형식이 잘못되었습니다.")
    except Exception as e:
        print(f"❌ [Thread-Error] 미션 수행 중 예상치 못한 오류 발생: {e}")
        traceback.print_exc()

@app.route('/start_mission', methods=['POST'])
def start_mission():
    """
    미션 시작을 위한 API 엔드포인트.
    이제 task 내용은 무시되고, 항상 sample_mission.json을 실행합니다.
    """
    data = request.json
    task = data.get('task', 'No task specified') # task가 없어도 오류 방지

    # 미션 실행을 별도의 스레드에서 비동기적으로 시작
    mission_thread = threading.Thread(target=run_mission_background, args=(task,))
    mission_thread.start()
    
    return jsonify({
        "status": "success",
        "message": f"'{task}' 요청을 접수했습니다. sample_mission.json을 기반으로 미션을 시작합니다.",
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

