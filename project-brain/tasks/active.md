# Active Task

## Phase 4 — LoopAgent + Report Agent + CLI

### Objectives
- Build `LoopAgent`: orchestrates Attack-Strategy Agent (Phase 2) and Evaluator Agent (Phase 3) in a self-correcting loop (max 5 iterations).
- Feed Evaluator failures back into Attack-Strategy Agent for adaptive payload refinement.
- Build `report_agent/agent.py`: `LlmAgent` that renders a structured Markdown red-team report from all harness + evaluator outputs.
- Build `redteam_cli.py`: CLI entry point (`glasshouse scan <target>`) that runs the full pipeline end-to-end.
- Update control-case validation: remove or correct the `direct_override → success: false` expectation in light of Phase 3 findings.

### Key Files to Create
- `loop_agent/agent.py`
- `report_agent/agent.py`
- `redteam_cli.py`
