# utils.py
import logging

def setup_logging():
    """기본 로깅 설정을 구성합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
    )
