#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import re
import time
from pathlib import Path
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

# -------------------
# Qwen 기반 PDDL 생성
# -------------------

def generate_pddl_from_text(llm, tokenizer, text: str, mode: str,
                            temperature: float=0.2, top_p: float=0.9, max_tokens: int=1024):
    domain_name = "uav"

    if mode == "problem":
        prompt_text = (
            f"Based on the following mission description, generate a valid PDDL problem file.\n"
            f"The domain name is '{domain_name}'.\n\n"
            f"Mission Description:\n{text}\n\n"
            "Output only valid PDDL syntax."
        )
    elif mode == "plan":
        prompt_text = (
            f"Given the following UAV domain and problem description, generate a valid PDDL plan.\n"
            f"Domain: {domain_name}\n\n"
            f"Problem Description:\n{text}\n\n"
            "Output only valid PDDL plan actions, one per line."
        )
    else:
        raise ValueError("Mode must be 'problem' or 'plan'")

    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )

    start_time = time.time()
    response = llm.generate([prompt_text], sampling_params=sampling_params)
    elapsed = time.time() - start_time

    output_text = response[0].outputs[0].text.strip()
    print(f"[INFO] {mode} generation done in {elapsed:.2f} sec")

    # <think> 제거 등 정리
    output_text = re.sub(r'<think>.*?</think>', '', output_text, flags=re.DOTALL).strip()
    return output_text


def main():
    parser = argparse.ArgumentParser(description="Generate PDDL problem and plan files using Qwen (vLLM).")
    parser.add_argument("prompt_file", help="Path to the natural language mission description file.")
    parser.add_argument("--model", type=str, default="Qwen/Qwen-7B", help="Qwen model name")
    parser.add_argument("--local_dir", type=str, default="./data/models", help="LLM local storage directory")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--max_tokens", type=int, default=1024)
    args = parser.parse_args()

    # base_dir를 prompt_file 기준으로 상대 경로 계산
    prompt_path = Path(args.prompt_file)
    base_dir = prompt_path.parent.parent.resolve()  # uav.qwen/prompts/... -> uav.qwen
    mission_dir = base_dir / "mission"
    plan_dir = base_dir / "plan"
    mission_dir.mkdir(parents=True, exist_ok=True)
    plan_dir.mkdir(parents=True, exist_ok=True)

    problem_path = mission_dir / "problem.pddl"
    plan_path = plan_dir / "plan.pddl"

    # --- Read mission prompt ---
    try:
        nl_prompt = prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        print(f"Error: Prompt file not found: {args.prompt_file}", file=sys.stderr)
        sys.exit(1)

    print(f"\nReading mission prompt from: {args.prompt_file}\n")
    print(nl_prompt)
    print("\n--- Generating PDDL files ---\n")

    # --- Initialize Qwen tokenizer and LLM ---
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    llm = LLM(
        model=args.model,
        download_dir=args.local_dir,
        dtype="bfloat16",
        seed=0,
        max_model_len=2048,
        gpu_memory_utilization=0.3,
        trust_remote_code=True   # <- 여기를 추가
)


    # --- Generate problem.pddl ---
    try:
        problem_pddl = generate_pddl_from_text(llm, tokenizer, nl_prompt, "problem",
                                               temperature=args.temperature,
                                               top_p=args.top_p,
                                               max_tokens=args.max_tokens)
        problem_path.write_text(problem_pddl, encoding="utf-8")
        print(f"Problem file saved to: {problem_path}")
    except Exception as e:
        print(f"Error generating problem PDDL: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Generate plan.pddl ---
    try:
        plan_pddl = generate_pddl_from_text(llm, tokenizer, problem_pddl, "plan",
                                            temperature=args.temperature,
                                            top_p=args.top_p,
                                            max_tokens=args.max_tokens)
        plan_path.write_text(plan_pddl, encoding="utf-8")
        print(f"Plan file saved to: {plan_path}")
    except Exception as e:
        print(f"Error generating plan PDDL: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nGeneration Complete")
    print(f"- Problem: {problem_path}")
    print(f"- Plan: {plan_path}")


if __name__ == "__main__":
    main()
