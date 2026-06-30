# Changelog

## 2026-06-29
- Phase 1 completed: MCP mock server + BookingBot agent + ADK Runner execution integrated
- Refactored execution from direct invocation to Runner-based async pipeline
- VULN-4 (over-privileged tool) added: `get_all_bookings_for_hotel` registered to LlmAgent without ownership check
- Mock booking data extended: Alice (B100, B300) and Bob (B200) share Grand Plaza hotel

## 2026-06-30
- Phase 2 completed: Standalone AttackStrategyAgent implemented and validated
- Supported 4 attack techniques: direct_override, roleplay_jailbreak, tool_description_poisoning, indirect_injection
- Added technique-to-vector mapping rules to system instructions
- Fixed injection_vector mapping bug for tool_description_poisoning
- All 4 techniques validated with test harness
- Updated brain.md with Phase 2 implementation notes
- Updated tasks/completed.md with Phase 2 summary
