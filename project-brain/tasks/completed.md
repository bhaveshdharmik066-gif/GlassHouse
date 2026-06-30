# Completed Tasks

## Phase 1 — Target System
**Status:** COMPLETED  
**Summary:** Vulnerable BookingBot with MCP-compatible tool layer + ADK Runner-based execution completed.  
**Delivered:**
- `target_vulnerable/local_mcp_adapter.py` — MCP mock adapter with in-memory bookings store
- `target_vulnerable/agent.py` — BookingBot `LlmAgent` with 4 tools registered
- `target_vulnerable/main.py` — Runner + async execution harness with manual test cases
- VULN-1, VULN-2, VULN-3, VULN-4 planted and manually verified
