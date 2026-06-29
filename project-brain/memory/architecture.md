# Architecture
1. **Target System**: Booking agent (`LlmAgent`) exposing tools via mock MCP server.
2. **Attack-Strategy Agent**: `LlmAgent` producing malicious payloads.
3. **Execution Harness**: Python orchestrator executing attacks.
4. **Evaluator Agent**: `LlmAgent` judging attack success.
5. **Report Agent + CLI**: Markdown report generation.
