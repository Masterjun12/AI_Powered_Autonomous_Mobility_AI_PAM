import argparse
import subprocess
import os
import sys


# --- Configuration ---
VALIDATOR_PATH = os.path.join(os.path.dirname(__file__), "downward", "validate")

# Windows에서 실행 시 .exe 자동 보정
if os.name == "nt" and not VALIDATOR_PATH.endswith(".exe"):
    VALIDATOR_PATH += ".exe"


# Windows에서 실행 시 .exe 자동 보정
if os.name == "nt" and not VALIDATOR_PATH.endswith(".exe"):
    VALIDATOR_PATH += ".exe"

DOMAIN_FILE = os.path.join(os.path.dirname(__file__), "domain.pddl")


def check_pddl(problem_file: str) -> bool:
    """Validates a PDDL problem file against the domain file."""
    
    # 파일 존재 확인
    if not os.path.exists(VALIDATOR_PATH):
        print(f"Error: Validator not found at {VALIDATOR_PATH}")
        print("Please ensure the 'downward' submodule is initialized and built.")
        return False

    if not os.path.exists(DOMAIN_FILE):
        print(f"Error: Domain file not found at {DOMAIN_FILE}")
        return False

    if not os.path.exists(problem_file):
        print(f"Error: Problem file not found at {problem_file}")
        return False

    print("\n--- Validating PDDL ---")
    print(f"Domain: {DOMAIN_FILE}")
    print(f"Problem: {problem_file}\n")

    try:
        # ./validate <domain.pddl> <problem.pddl>
        result = subprocess.run(
            [VALIDATOR_PATH, DOMAIN_FILE, problem_file],
            capture_output=True,
            text=True,
            check=True
        )

        # 결과 통합
        output = (result.stdout or "") + (result.stderr or "")

        if "Problem file is a valid instance of domain" in output:
            print("PDDL validation successful.")
            return True
        else:
            print("PDDL validation failed. Details below:\n")
            print(output.strip())
            return False

    except subprocess.CalledProcessError as e:
        print(f"Validation process failed (exit code {e.returncode})")
        if e.stdout:
            print("STDOUT:\n", e.stdout)
        if e.stderr:
            print("STDERR:\n", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Could not execute validator at '{VALIDATOR_PATH}'. Please check the path.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a PDDL problem file.")
    parser.add_argument("problem_file", help="Path to the PDDL problem file to validate.")
    args = parser.parse_args()

    success = check_pddl(args.problem_file)
    sys.exit(0 if success else 1)
