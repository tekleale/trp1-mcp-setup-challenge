# LangGraph State Machine

## Overview

This module implements the state machine skeleton for orchestrating Planner-Worker-Judge agent workflows in Project Chimera.

## State Machine Structure

### States

1. **Init**
   - Purpose: Initialize session and prepare for task execution
   - Entry: Workflow starts or completes
   - Exit: Transition to ExecuteTask

2. **ExecuteTask**
   - Purpose: Worker agent executes next task from queue
   - Entry: From Init or EvaluateResult (if more tasks pending)
   - Exit: Transition to EvaluateResult or back to Init (if queue empty)

3. **EvaluateResult**
   - Purpose: Judge agent assesses quality and determines HITL routing
   - Entry: From ExecuteTask (after task completion)
   - Exit: Transition to ExecuteTask (if approved) or Init (if workflow complete)

### Allowed Transitions

```
Init → ExecuteTask
ExecuteTask → EvaluateResult
ExecuteTask → ExecuteTask (retry)
EvaluateResult → ExecuteTask (more tasks)
EvaluateResult → Init (workflow complete)
```

### HITL Integration

The EvaluateResult state implements the three-tier approval system:
- confidence > 0.90: Auto-approve, continue to next task
- 0.70 ≤ confidence ≤ 0.90: HITL interrupt (human review required)
- confidence < 0.70: Auto-reject, retry or skip task

## Implementation Status

**Current:** Skeleton with method stubs and docstrings  
**Next Steps:** Implement agent calls (Planner, Worker, Judge) and integrate with LangGraph library

## Spec References

- specs/technical.md Section 3 (LangGraph State Machine)
- specs/functional.md Section 2 (Agent Roles)
- specs/functional.md Section 3 (HITL Workflow)

