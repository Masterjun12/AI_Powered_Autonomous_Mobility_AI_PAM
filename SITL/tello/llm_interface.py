# llm_interface.py

import google.generativeai as genai
import config
import logging
import json
from prompts import SYSTEM_PROMPT

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --- 실제 API 설정 ---
try:
    genai.configure(api_key=config.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    logging.info("Google AI SDK가 성공적으로 설정되었습니다.")
except Exception as e:
    logging.error(f"Google AI SDK 설정에 실패했습니다. API 키를 확인하세요: {e}")
    model = None
# ----------------------------------------

def get_drone_command(query: str) -> dict:
    """
    사용자의 자연어 쿼리를 받아 LLM을 통해 JSON 형식의 드론 명령어로 변환합니다.
    """
    if not model:
        logging.error("LLM 모델이 초기화되지 않았습니다.")
        return {"command": "error", "parameters": {"reason": "LLM model not initialized"}}

    try:
        # 프롬프트와 사용자 쿼리를 함께 전달
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: \"{query}\"\nAssistant:"
        
        # --- 실제 API 호출 ---
        response = model.generate_content(full_prompt)
        # 응답 텍스트에서 JSON 부분만 추출 (예: ```json ... ``` 제거)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        # ------------------

        logging.info(f"LLM 응답: {cleaned_response}")
        return json.loads(cleaned_response)
    
    except json.JSONDecodeError as e:
        logging.error(f"LLM 응답 JSON 파싱 오류: {e}")
        return {"command": "error", "parameters": {"reason": "LLM 응답 파싱 오류"}}
    except Exception as e:
        logging.error(f"LLM API 호출 중 오류 발생: {e}")
        return {"command": "error", "parameters": {"reason": f"LLM API call failed: {e}"}}