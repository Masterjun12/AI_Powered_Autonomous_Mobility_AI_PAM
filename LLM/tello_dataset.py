
import json

def create_tello_dataset():
    """
    Tello 명령어와 한국어 질문을 매핑하는 데이터셋을 생성합니다.
    """
    command_map = {
        "takeoff": ["이륙해", "드론 띄워", "날아올라"],
        "land": ["착륙해", "드론 내려", "땅으로"],
        "streamon": ["영상 켜", "스트리밍 시작", "카메라 켜"],
        "streamoff": ["영상  꺼", "스트리밍 중지", "카메라 꺼"],
        "emergency": ["비상 정지", "모터 꺼", "긴급 상황"],
        "up": ["올라가", "위로", "상승해"],
        "down": ["내려가", "아래로", "하강해"],
        "left": ["왼쪽으로", "좌측으로"],
        "right": ["오른쪽으로", "우측으로"],
        "forward": ["앞으로", "전진"],
        "back": ["뒤로", "후진"],
        "cw": ["시계 방향으로 돌아", "오른쪽으로 회전"],
        "ccw": ["반시계 방향으로 돌아", "왼쪽으로 회전"],
        "flip": ["공중제비", "플립"],
        "stop": ["정지", "멈춰", "그 자리에 있어"],
    }

    dataset = []
    for command, questions in command_map.items():
        for question in questions:
            # Add variations for commands with parameters
            if command in ["up", "down", "left", "right", "forward", "back", "cw", "ccw"]:
                for i in range(20, 101, 20):
                    dataset.append({
                        "instruction": f"{question} {i}센티미터",
                        "input": "",
                        "output": f"{command} {i}"
                    })
            elif command == "flip":
                for direction_kr, direction_en in [("왼쪽", "l"), ("오른쪽", "r"), ("앞", "f"), ("뒤", "b")]:
                     dataset.append({
                        "instruction": f"{direction_kr}으로 {question}",
                        "input": "",
                        "output": f"{command} {direction_en}"
                    })
            else:
                dataset.append({
                    "instruction": question,
                    "input": "",
                    "output": command
                })

    # Example for "go" and "curve" commands (simplified)
    dataset.append({
        "instruction": "x 50, y 60, z 70 위치로 속도 80으로 이동해",
        "input": "",
        "output": "go 50 60 70 80"
    })
    dataset.append({
        "instruction": "x1 50, y1 60, z1 70 에서 x2 100, y2 90, z2 80 으로 속도 40으로 커브 비행해",
        "input": "",
        "output": "curve 50 60 70 100 90 80 40"
    })


    with open("tello_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    create_tello_dataset()
    print("Tello 데이터셋 생성 완료: tello_dataset.json")

