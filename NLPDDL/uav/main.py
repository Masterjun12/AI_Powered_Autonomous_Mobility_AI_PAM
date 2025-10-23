import os
import sys
import argparse
import google.generativeai as genai

def generate_pddl(model, nl_description, domain_name, mode):
    """Generate PDDL (problem or plan) from a natural language description."""
    if mode == "problem":
        prompt = (
            f"Based on the following mission description, generate a valid PDDL problem file.\n"
            f"The domain name is \"{domain_name}\".\n\n"
            f"Mission Description:\n{nl_description}\n\n"
            "Output only a valid PDDL problem definition."
        )
    elif mode == "plan":
        prompt = (
            f"Given the following domain and problem descriptions, generate a valid PDDL plan.\n"
            f"Domain: {domain_name}\n\n"
            f"Problem Description:\n{nl_description}\n\n"
            "Output only a valid plan with PDDL actions, one per line."
        )
    else:
        raise ValueError("Mode must be 'problem' or 'plan'")

    response = model.generate_content(prompt)
    return (response.text or "").strip()


def main():
    parser = argparse.ArgumentParser(description="Generate PDDL problem and plan files using Google Gemini.")
    parser.add_argument("prompt_file", help="Path to the natural language mission description file.")
    args = parser.parse_args()

    base_dir = "/home/a202520153/202520153/NLPDDL/uav"
    mission_dir = os.path.join(base_dir, "mission")
    plan_dir = os.path.join(base_dir, "plan")

    os.makedirs(mission_dir, exist_ok=True)
    os.makedirs(plan_dir, exist_ok=True)

    problem_path = os.path.join(mission_dir, "problem.pddl")
    plan_path = os.path.join(plan_dir, "plan.pddl")

    # --- Read Natural Language Input ---
    try:
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            nl_prompt = f.read().strip()
    except FileNotFoundError:
        print(f"Error: Prompt file not found: {args.prompt_file}", file=sys.stderr)
        sys.exit(1)

    print(f"\nReading mission prompt from: {args.prompt_file}\n")
    print(nl_prompt)
    print("\n--- Generating PDDL files ---\n")

    # --- API Configuration ---
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not set. Use: export GOOGLE_API_KEY=your_key", file=sys.stderr)
        sys.exit(1)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-flash-latest')
    except Exception as e:
        print(f"Error initializing Google AI: {e}", file=sys.stderr)
        sys.exit(1)

    domain_name = "uav"

    # --- Generate problem.pddl ---
    try:
        problem_pddl = generate_pddl(model, nl_prompt, domain_name, "problem")
        with open(problem_path, "w", encoding="utf-8") as f:
            f.write(problem_pddl)
        print(f"Problem file saved to: {problem_path}")
    except Exception as e:
        print(f"Error generating problem PDDL: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Generate plan.pddl ---
    try:
        plan_pddl = generate_pddl(model, problem_pddl, domain_name, "plan")
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(plan_pddl)
        print(f"Plan file saved to: {plan_path}")
    except Exception as e:
        print(f"Error generating plan PDDL: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nGeneration Complete")
    print(f"- Problem: {problem_path}")
    print(f"- Plan: {plan_path}")

if __name__ == "__main__":
    main()
