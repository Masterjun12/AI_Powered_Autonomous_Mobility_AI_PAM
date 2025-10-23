#!/bin/bash
set -e

# --- Configuration ---
export GOOGLE_API_KEY="AIzaSyAi6s-980hODG2kg_hp0ZKaR7h4cqkmw68"

BASE_DIR="/home/a202520153/202520153/NLPDDL/uav"
PROMPT_FILE="$BASE_DIR/prompts/p_example.nl"  # 여기를 올바른 프롬프트 파일로 수정

# --- Main Execution ---
echo "Checking for GOOGLE_API_KEY..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable is not set."
    exit 1
fi
echo "API key found."

echo -e "\nStep 1: Generating PDDL problem and plan..."
python3 "$BASE_DIR/main.py" "$PROMPT_FILE"

# Optional: Validate problem.pddl
PROBLEM_FILE="$BASE_DIR/mission/problem.pddl"
if [ -f "$PROBLEM_FILE" ]; then
    echo -e "\nStep 2: Validating generated problem PDDL..."
    python3 "$BASE_DIR/check_pddl.py" "$PROBLEM_FILE"
else
    echo "Problem file not found. Skipping validation."
fi

echo -e "\nAll steps completed successfully."
echo "Generated files:"
echo "- Problem: $BASE_DIR/mission/problem.pddl"
echo "- Plan   : $BASE_DIR/plan/plan.pddl"
