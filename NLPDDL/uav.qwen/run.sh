#!/bin/bash
set -e

# --- Auto-detect base directory ---
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$BASE_DIR/prompts/p_example.nl"

# --- Main Execution ---
echo -e "\nStep 1: Generating PDDL problem and plan using Qwen (vLLM)..."
python3 "$BASE_DIR/main.py" "$PROMPT_FILE"

# Optional: Validate problem.pddl using check_pddl.py
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
