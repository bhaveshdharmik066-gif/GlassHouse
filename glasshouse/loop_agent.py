"""
glasshouse/loop_agent.py
Phase 4A — LoopAgent pipeline

Iterative attack loop per technique, invoking AttackStrategyAgent, Harness, EvaluatorAgent.
"""

import asyncio
import json
import time
from typing import Any, Callable

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from attack_agent.agent import create_attack_agent
from execution_harness.harness import run_attack_async
from evaluator_agent.agent import create_evaluator_agent
from glasshouse.targets import TARGETS

MAX_ITERATIONS = 5
INTER_TECHNIQUE_SLEEP = 15

async def _query_agent(agent, app_name: str, session_id: str, user_content: str) -> str:
    """Helper to run an ADK LlmAgent for a single turn and return raw text."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name, user_id="tester", session_id=session_id
    )
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

    response_text = ""
    for attempt in range(1, 6):
        try:
            async for event in runner.run_async(
                user_id="tester",
                session_id=session_id,
                new_message=types.Content(
                    role="user", parts=[types.Part.from_text(text=user_content)]
                ),
            ):
                if event.is_final_response():
                    if getattr(event, "error", None):
                        raise RuntimeError(f"Agent error: {event.error}")
                    if event.content and getattr(event.content, "parts", None):
                        response_text = event.content.parts[0].text
            break
        except Exception as exc:
            if "503" in str(exc) or "429" in str(exc):
                print(f"  [API Error: {exc}]. Retrying in 10s (attempt {attempt}/5)...")
                time.sleep(10)
            else:
                raise

    return response_text

async def run_loop_async(target_name: str, progress_callback: Callable = None, single_technique: str = None) -> list[dict]:
    """
    Runs the full attack loop across all techniques for a target.
    
    progress_callback signature:
        (technique: str, iteration: int, verdict: dict, exit_reason: str|None)
    """
    if target_name not in TARGETS:
        raise ValueError(f"Unknown target: {target_name}")
    
    target_config = TARGETS[target_name]
    target_description = target_config["description"]
    techniques = target_config["techniques"]
    if single_technique:
        techniques = [single_technique]
    
    attack_agent = create_attack_agent()
    evaluator_agent = create_evaluator_agent()
    
    attack_log = []
    
    for t_idx, technique in enumerate(techniques):
        if t_idx > 0:
            if progress_callback:
                # We can just let the callback know we are sleeping if needed, 
                # but standard sleeping is fine.
                pass
            time.sleep(INTER_TECHNIQUE_SLEEP)
            
        prior_attempt = None
        prior_feedback = None
        exit_reason = None
        
        try:
            for iteration in range(1, MAX_ITERATIONS + 1):
                is_final_iteration = (iteration == MAX_ITERATIONS)
                
                # 1. Attack-Strategy Agent
                attack_input = {
                    "target_description": target_description,
                    "technique": technique,
                    "prior_attempt": prior_attempt,
                    "prior_feedback": prior_feedback
                }
                
                session_id = f"attack-{technique}-{iteration}"
                raw_payload = await _query_agent(
                    attack_agent, "AttackStrategyAgent", session_id, json.dumps(attack_input)
                )
                
                # Note: We assume the agent returned valid JSON, per previous phase's validation pattern.
                try:
                    # Strip markdown code blocks if present
                    clean_payload = raw_payload.strip()
                    if clean_payload.startswith("```"):
                        clean_payload = clean_payload.split("\n", 1)[-1]
                        if clean_payload.startswith("json"):
                            clean_payload = clean_payload[4:].strip()
                    if clean_payload.endswith("```"):
                        clean_payload = clean_payload.rsplit("\n", 1)[0]
                    
                    payload = json.loads(clean_payload.strip())
                except json.JSONDecodeError as exc:
                    # If it breaks, we just log failure and stop this technique
                    print(f"Error parsing attack payload: {exc}\nRaw: {raw_payload}")
                    raise Exception(f"Failed to parse attack payload: {exc}")
                    
                # 2. Execution Harness
                harness_result = await run_attack_async(payload)
                
                # 3. Evaluator Agent
                eval_session_id = f"eval-{technique}-{iteration}"
                # Evaluator input is exactly the harness result
                raw_verdict = await _query_agent(
                    evaluator_agent, "EvaluatorAgent", eval_session_id, json.dumps(harness_result)
                )
                
                try:
                    clean_verdict = raw_verdict.strip()
                    if clean_verdict.startswith("```"):
                        clean_verdict = clean_verdict.split("\n", 1)[-1]
                        if clean_verdict.startswith("json"):
                            clean_verdict = clean_verdict[4:].strip()
                    if clean_verdict.endswith("```"):
                        clean_verdict = clean_verdict.rsplit("\n", 1)[0]
                    verdict = json.loads(clean_verdict.strip())
                except json.JSONDecodeError as exc:
                    print(f"Error parsing evaluator verdict: {exc}\nRaw: {raw_verdict}")
                    raise Exception(f"Failed to parse evaluator verdict: {exc}")
                    
                # Check exit conditions
                if verdict.get("success", False):
                    exit_reason = "success"
                    is_final_iteration = True
                elif is_final_iteration:
                    exit_reason = "max_iterations_reached"
                    
                # Log this iteration
                entry = {
                    "technique": technique,
                    "iteration": iteration,
                    "payload": payload,
                    "harness_result": harness_result,
                    "verdict": verdict,
                    "exit_reason": exit_reason if is_final_iteration else None
                }
                attack_log.append(entry)
                
                if progress_callback:
                    progress_callback(
                        technique, 
                        iteration, 
                        verdict, 
                        exit_reason if is_final_iteration else None
                    )
                    
                if exit_reason:
                    break
                    
                # Prepare for retry
                prior_attempt = payload
                prior_feedback = verdict.get("evidence", "No evidence provided")
        except Exception as exc:
            current_iteration = iteration if 'iteration' in locals() else 1
            error_entry = {
                "technique": technique,
                "iteration": current_iteration,
                "payload": prior_attempt,
                "harness_result": None,
                "verdict": None,
                "exit_reason": "error",
                "error": str(exc)
            }
            attack_log.append(error_entry)
            if progress_callback:
                progress_callback(technique, current_iteration, {}, "error")
            
    return attack_log

def run_loop(target_name: str, progress_callback: Callable = None, single_technique: str = None) -> list[dict]:
    return asyncio.run(run_loop_async(target_name, progress_callback, single_technique))

if __name__ == "__main__":
    import sys
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv(override=True)
    
    parser = argparse.ArgumentParser(description="Standalone LoopAgent test")
    parser.add_argument("--technique", type=str, help="Run a single technique in isolation", default=None)
    args = parser.parse_args()
    
    def demo_callback(technique, iteration, verdict, exit_reason):
        status = "SUCCESS" if verdict.get("success") else "no exploit"
        msg = f"  Iteration {iteration}/{MAX_ITERATIONS}... {status}"
        if verdict.get("success"):
            msg += f" ({verdict.get('severity', 'unknown')} severity)"
        
        if exit_reason == "max_iterations_reached":
            msg = f"  Iteration {iteration}/{MAX_ITERATIONS}... max iterations reached"
            
        print(msg)
        
        # Only print technique header on iteration 1
        # In a real CLI we might structure this better, but this is just for the Checkpoint 1 standalone test
        pass
        
    print("Running standalone LoopAgent test...")
    
    # Wrap callback to print technique headers cleanly
    current_tech = None
    tech_idx = 1
    def cb(tech, it, verdict, reason):
        global current_tech, tech_idx
        if tech != current_tech:
            print(f"[{tech_idx}/4] Testing: {tech}")
            current_tech = tech
            tech_idx += 1
        demo_callback(tech, it, verdict, reason)

    # We only run against a subset if we don't want to wait 4 mins, but specs say "confirm the loop runs all 4 techniques"
    log = run_loop("booking_bot", cb, single_technique=args.technique)
    
    print("\n--- RAW ATTACK LOG ---")
    
    # Strip raw_trace for printing so it fits in context easily
    import copy
    print_log = copy.deepcopy(log)
    for entry in print_log:
        if "raw_trace" in entry.get("harness_result", {}):
            del entry["harness_result"]["raw_trace"]
            
    print(json.dumps(print_log, indent=2))
