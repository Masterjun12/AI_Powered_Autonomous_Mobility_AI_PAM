# llm_interface.py
import google.generativeai as genai
import config
import logging
from prompts import SYSTEM_PROMPT

# API 키 설정
try:
    genai.configure(api_key=config.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemma-3-27b-it')
except Exception as e:
    logging.error(f"Google AI SDK 설정에 실패했습니다. API 키를 확인하세요: {e}")
    model = None
    
def get_drone_command(query: str) -> str:
    """
    사용자의 자연어 쿼리를 받아 LLM을 통해 JSON 형식의 드론 명령어로 변환합니다.
    """
    
    if not model:
        logging.error("LLM 모델이 초기화되지 않았습니다.")
        return '{"error": "LLM model not initialized"}'

    try:
        # 프롬프트와 사용자 쿼리를 함께 전달
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: \"{query}\"\nAssistant:"
        response = model.generate_content(full_prompt)
        
        # 응답 텍스트에서 JSON 부분만 추출
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        logging.info(f"LLM 응답: {cleaned_response}")
        return cleaned_response
    except Exception as e:
        logging.error(f"LLM API 호출 중 오류 발생: {e}")
        return f'{{"error": "LLM API call failed: {e}"}}'