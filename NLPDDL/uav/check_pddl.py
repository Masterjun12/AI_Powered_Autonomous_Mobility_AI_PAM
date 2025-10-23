import argparse
import os
import sys

DOMAIN_FILE = os.path.join(os.path.dirname(__file__), "domain.pddl")

def check_pddl(problem_file: str) -> bool:
    """Simple PDDL syntax check: existence + minimal format check"""
    
    # 파일 존재 확인
    if not os.path.exists(DOMAIN_FILE):
        print(f"Error: Domain file not found at {DOMAIN_FILE}")
        return False

    if not os.path.exists(problem_file):
        print(f"Error: Problem file not found at {problem_file}")
        return False

    # 최소 문법 체크: define (problem ...) 포함 여부
    try:
        with open(problem_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if "(define (problem" not in content:
            print("PDDL validation failed: '(define (problem ...' not found.")
            return False
    except Exception as e:
        print(f"Error reading problem file: {e}")
        return False

    print("PDDL validation passed (basic check).")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a PDDL problem file (basic check).")
    parser.add_argument("problem_file", help="Path to the PDDL problem file to validate.")
    args = parser.parse_args()

    success = check_pddl(args.problem_file)
    sys.exit(0 if success else 1)
