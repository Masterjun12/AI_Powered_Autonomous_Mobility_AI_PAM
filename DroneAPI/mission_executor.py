# mission_executor.py
from typing import List, Dict
from drone_api import DroneTimeBasedAPI

class MissionExecutor:
    """
    LLM이 생성한 미션 계획(command list)을 받아
    드론 API를 통해 순차적으로 실행하는 클래스.
    """
    def __init__(self, drone_api: DroneTimeBasedAPI):
        self.drone = drone_api
        print("💡 [Executor] 미션 실행기가 준비되었습니다.")

    def execute_mission(self, commands: List[Dict]):
        """명령어 리스트를 받아 순차적으로 실행합니다."""
        print("\n" + "="*20 + " 미션 실행 시작 " + "="*20)
        
        # vllm_agent.py의 최종 출력 형식은 [[{...}, {...}]] 일 수 있으므로,
        # 중첩된 리스트를 풀어 단일 리스트로 만듭니다.
        flat_commands = []
        if commands and isinstance(commands[0], list):
             for sublist in commands:
                flat_commands.extend(sublist)
        else:
            flat_commands = commands

        for i, cmd_dict in enumerate(flat_commands):
            if not isinstance(cmd_dict, dict):
                print(f"⚠️ [Executor-Warning] 잘못된 명령어 형식입니다: {cmd_dict}. 건너뜁니다.")
                continue

            command_name = cmd_dict.get("command")
            params = cmd_dict.get("parameters", {})
            
            if not command_name:
                print(f"⚠️ [Executor-Warning] 'command' 키가 없는 항목입니다: {cmd_dict}. 건너뜁니다.")
                continue
            
            print(f"\n[스텝 {i+1}/{len(flat_commands)}] >> {command_name.upper()} 실행")
            
            try:
                # getattr을 이용해 drone_api에서 이름에 맞는 함수를 찾아 실행
                func_to_call = getattr(self.drone, command_name)
                func_to_call(**params)
            except AttributeError:
                print(f"❓ [Executor-Warning] '{command_name}'에 해당하는 API 함수를 찾을 수 없습니다.")
            except Exception as e:
                print(f"❌ [Executor-Error] '{command_name}' 실행 중 오류 발생: {e}. 미션을 중단합니다.")
                break
        
        print("\n" + "="*20 + " 모든 미션 완료 " + "="*21 + "\n")