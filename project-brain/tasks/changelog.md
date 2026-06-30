# Changelog

## 2026-06-29
- Phase 1 completed: MCP mock server + BookingBot agent + ADK Runner execution integrated
- Refactored execution from direct invocation to Runner-based async pipeline
- VULN-4 (over-privileged tool) added: `get_all_bookings_for_hotel` registered to LlmAgent without ownership check
- Mock booking data extended: Alice (B100, B300) and Bob (B200) share Grand Plaza hotel
