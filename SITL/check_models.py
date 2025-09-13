
import google.generativeai as genai
import config
import logging

# 기본 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def list_available_models():
    """
    Google AI API를 설정하고 사용 가능한 모든 모델 목록을 출력합니다.
    특히 'generateContent'를 지원하는 모델을 강조 표시합니다.
    """
    try:
        # config.py에서 API 키를 가져와 설정
        if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY":
            print("오류: config.py 파일에 Google API 키가 설정되지 않았습니다.")
            print("파일을 열고 GOOGLE_API_KEY 변수에 유효한 키를 입력해주세요.")
            return

        genai.configure(api_key=config.GOOGLE_API_KEY)
        logging.info("Google AI API 설정 완료.")

        print("\n--- 사용 가능한 모델 목록 ---")
        models_found = False
        for model in genai.list_models():
            models_found = True
            # 챗봇에 필요한 'generateContent' 메소드를 지원하는지 확인
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - 모델 이름: {model.name}")
                print(f"    지원하는 메소드: {model.supported_generation_methods}\n")
        
        if not models_found:
            print("사용 가능한 모델을 찾을 수 없습니다. API 키 또는 네트워크 연결을 확인하세요.")

    except Exception as e:
        logging.error(f"API 키 설정 또는 모델 목록 조회 중 오류가 발생했습니다: {e}")
        print("\n오류: API 키가 유효한지, 또는 config.py에 올바르게 입력되었는지 확인해 주세요.")
        print("오류 메시지:", str(e))

if __name__ == "__main__":
    list_available_models()
