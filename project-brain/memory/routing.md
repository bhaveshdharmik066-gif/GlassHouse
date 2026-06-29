# Routing (Inter-Agent Data Flow)
- Attack-Strategy -> Harness
- Harness -> Evaluator
- Evaluator -> Attack-Strategy (if failed and iterations < 5 via LoopAgent)
- LoopAgent -> Report Agent
