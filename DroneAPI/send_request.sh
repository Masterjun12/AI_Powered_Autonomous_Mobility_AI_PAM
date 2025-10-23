# send_request.sh
#!/bin-bash

# API 서버의 주소
API_URL="http://127.0.0.1:5001/start_mission"

# API로 보낼 자연어 임무 (이 부분을 자유롭게 수정하여 테스트하세요)
TASK_TO_RUN="Take off, go forward 100 cm, rotate clockwise 90 degrees, and then land."

echo "========================================="
echo " API 서버에 미션 요청 전송"
echo "========================================="
echo "URL: $API_URL"
echo "TASK: '$TASK_TO_RUN'"
echo "-----------------------------------------"

# curl을 사용하여 POST 요청 전송
curl -X POST \
     -H "Content-Type: application/json" \
     -d "{\"task\": \"$TASK_TO_RUN\"}" \
     $API_URL

echo -e "\n\n요청을 보냈습니다. 서버가 실행된 터미널에서 실행 로그를 확인하세요."