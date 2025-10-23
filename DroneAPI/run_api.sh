# run_api.sh
#!/bin/bash

echo "========================================="
echo " LLM Drone API 서버 시작"
echo "========================================="
echo "PORT: 5001"
echo "서버가 준비되면 다른 터미널에서 send_request.sh를 실행하여 테스트하세요."
echo "-----------------------------------------"

# 필요한 라이브러리 설치 (최초 1회)
pip install flask

# 기존 run.sh와 동일하게 CUDA 디바이스 설정
export CUDA_VISIBLE_DEVICES=2

# API 서버 실행
python api_server.py