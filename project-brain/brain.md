# Glasshouse Project Brain

## Project Vision
An automated red-teaming framework where one AI agent generates prompt-injection attacks, fires them at a target AI agent, evaluates whether the attack succeeded, and produces a report with the exact vulnerable line and a suggested fix. Demonstrates that AI agent guardrails can be tested automatically and repeatably.

## Architecture Overview
Five components: Target System (mock MCP server + BookingBot), Attack-Strategy Agent, Execution Harness, Evaluator Agent, Report Agent + CLI.

## System Components & Agent Responsibilities
- **Target System**: "BookingBot" built with `LlmAgent` + tools via mock MCP server. Has deliberately planted vulnerabilities.
- **Attack-Strategy Agent**: `LlmAgent` that generates concrete attack payloads (direct_override, roleplay_jailbreak, tool_description_poisoning, indirect_injection).
- **Execution Harness**: Plain Python script that executes the Attack-Strategy payload against the Target System and captures trace.
- **Evaluator Agent**: `LlmAgent` that judges attack success based on unauthorized tool call, guardrail bypass, or data leak. Wired with Attack-Strategy in a `LoopAgent`.
- **Report Agent + CLI**: `LlmAgent` or template renderer that outputs Markdown report. CLI `glasshouse scan <target>`.

## Data Contracts
- **Attack-Strategy Input**: `{target_description: str, technique: str, prior_attempt: Optional[dict], prior_feedback: Optional[str]}`
- **Attack-Strategy Output**: `{technique: str, payload: str, injection_vector: str, hypothesis: str}`
- **Harness Output**: `{attack_payload: dict, target_response: str, tool_calls: list[dict], raw_trace: list}`
- **Evaluator Output**: `{success: bool, criteria_triggered: list[str], evidence: str, severity: "low"|"medium"|"high"}`

## Folder Ownership
- `target_vulnerable/`: Target agent with guardrails off.
- `target_defended/`: Target agent with ADK callbacks/guardrails.
- `out/`: Output directory for `report.md` and `attack_log.json`.
- `project-brain/`: Project Brain for AI memory and planning.

## Runtime Workflow
1. CLI invoked: `glasshouse scan <path_to_target_agent>`
2. LoopAgent initialized with Attack-Strategy and Evaluator Agents (max 5 iterations).
3. Attack-Strategy generates payload.
4. Harness executes payload against Target.
5. Evaluator judges success. If success or max iter, exit loop.
6. Report Agent generates report.

## Build Phases
1. **Target System**: `target_vulnerable/` with 4 planted vulnerabilities.
2. **Attack-Strategy Agent**: Standalone agent with test harness.
3. **Execution Harness + Evaluator Agent**: Wire harness to evaluator.
4. **LoopAgent wiring + Report Agent + CLI**: End-to-end integration.
5. **Defended target**: `target_defended/` with guardrails patched.

## Security Principles
- Keep all secrets in `.env`, never hardcoded.
- Demo-safe code: no real targets, mock data only, no exfiltration.

## Coding Standards
- Python 3.10+
- `google-adk` framework
- Explicit structured JSON outputs where specified.

## Testing Strategy
- Manual test for Phase 1.
- Standalone test harness for Phase 2.
- Manual verification of Evaluator in Phase 3.
- End-to-end automated test via CLI in Phase 4.

## Deployment Notes
- Local execution via CLI. Zero manual setup steps beyond `pip install -r requirements.txt` and `.env`.

## Known Limitations
- Mock target systems only.

## TODO Registry
- Phase 1: Build target_vulnerable/
- Phase 2: Build Attack-Strategy Agent
- Phase 3: Build Harness + Evaluator
- Phase 4: Build LoopAgent + CLI
- Phase 5: Build target_defended/
