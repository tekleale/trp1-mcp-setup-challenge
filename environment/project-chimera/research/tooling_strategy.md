# Project Chimera: Developer Tooling Strategy

**Version:** 0.1.0  
**Status:** Design Document  
**Purpose:** Define Developer MCP tools that support Spec-Driven Development and traceability  
**Last Updated:** 2026-02-06

---

## 1. Overview

### 1.1 Purpose of This Document

This document defines **Developer MCP tools** - tools used during development to support Spec-Driven Development (SDD), debugging, and observability. These are distinct from:
- **Runtime MCP servers** (used by agents during execution, e.g., Twitter API)
- **Agent Skills** (internal capabilities, defined in `skills/README.md`)

### 1.2 Developer Tools vs Runtime Tools

| Aspect | Developer MCP Tools | Runtime MCP Servers |
|--------|---------------------|---------------------|
| **Audience** | Human developers, AI coding assistants | Autonomous agents (Planner, Worker, Judge) |
| **Lifecycle** | Development, debugging, testing | Production execution |
| **Examples** | Spec validator, state inspector | Twitter API, Tenx Sense |
| **Integration** | IDE (Cursor, VS Code) | Agent orchestration layer |

### 1.3 How Tooling Supports SDD and Traceability

**Spec-Driven Development (SDD) Workflow:**
1. Human/AI reads specs (`specs/functional.md`, `specs/technical.md`)
2. Human/AI implements code
3. **Developer MCP tools validate compliance** (Spec Validator MCP)
4. **Developer MCP tools inspect runtime behavior** (State Inspector MCP)
5. **Developer MCP tools verify traceability** (Tenx Sense MCP)
6. Human/AI commits with spec references

**Traceability Requirements (FR 4.0):**
- Every agent action must be logged to Tenx MCP Sense
- Every state transition must be traceable
- Every MCP call must include `trace_id`
- Developer tools provide visibility into this traceability chain

---

## 2. Developer MCP Tools (Not Runtime)

### 2.1 Tenx MCP Sense (Feedback Analytics)

**Status:** ✅ Already Configured (`.vscode/mcp.json`)

**Name:** `tenxfeedbackanalytics`

**Purpose:**  
Traceability and feedback analytics for all agent actions. Required by SRS FR 4.0: "All agent actions must be logged to the Tenx MCP Sense server for traceability and feedback analytics."

**Why MCP (Not a Skill):**
- **External service:** Hosted at `https://mcppulse.10academy.org/proxy`
- **Standardized interface:** Uses MCP protocol for logging
- **Development + Runtime:** Used during development for debugging AND runtime for production logging
- **Observability:** Provides structured access to agent action history

**How It Supports Traceability:**
- Every agent action (planner_start, worker_complete, judge_evaluate) logs to Tenx Sense
- Each log includes: `session_id`, `action_type`, `metadata`, `timestamp`, `trace_id`
- Developers can query logs via MCP Resources: `tenx://feedback/sessions`, `tenx://feedback/session/{id}`
- Enables end-to-end tracing of agent workflows

**How It Supports SDD:**
- Validates that specs are being followed in practice
- Example: If specs require HITL at confidence < 0.90, Tenx logs show actual HITL trigger rates
- Provides feedback loop: Spec → Implementation → Logs → Spec refinement

**Configuration (from `.vscode/mcp.json`):**
```json
{
  "mcpServers": {
    "tenxfeedbackanalytics": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "env": {
        "TENX_MCP_URL": "https://mcppulse.10academy.org/proxy",
        "TENX_API_KEY": "${TENX_API_KEY}"
      }
    }
  }
}
```

**MCP Primitives:**

**Tools:**
- `tenx_log_action` - Log agent action
  - **Parameters:** `{session_id: str, action_type: str, metadata: dict, timestamp: str}`
  - **Returns:** `{logged: bool, trace_id: str}`
  - **Usage:** Called by every agent node (planner, worker, judge)

- `tenx_query_sessions` - Query logged sessions
  - **Parameters:** `{start_date: str, end_date: str, action_type: str | None}`
  - **Returns:** `{sessions: list[SessionSummary]}`
  - **Usage:** Developers query agent behavior patterns

**Resources:**
- `tenx://feedback/sessions` - List all logged sessions
- `tenx://feedback/session/{id}` - Get detailed session logs
- `tenx://feedback/actions/{action_type}` - Filter by action type

**Prompts:**
- None required for Phase 1

**Spec References:**
- `specs/technical.md` Section 5.1 (Tenx Sense Connection)
- `specs/technical.md` Section 10.1 (Tenx MCP Sense Integration)
- `specs/functional.md` Section 4.1 (Required MCP Servers)

---

### 2.2 Spec Validator MCP (Proposed)

**Status:** 🔮 Proposed for Future Implementation

**Name:** `chimera-spec-validator`

**Purpose:**  
Validate code compliance with specifications during development. Provides real-time feedback to developers and AI coding assistants when code deviates from `specs/`.

**Why MCP (Not a Skill):**
- **Developer-facing:** Used during development, not by agents at runtime
- **IDE integration:** Integrates with Cursor/VS Code for real-time validation
- **Standardized interface:** MCP provides structured validation results
- **Separation of concerns:** Validation logic separate from agent logic

**How It Supports Traceability:**
- Links code implementations to specific spec sections
- Generates traceability matrix: Code file → Spec section → SRS requirement
- Validates that all spec requirements have corresponding implementations

**How It Supports SDD:**
- **Pre-commit validation:** Check if Pydantic schemas match `specs/technical.md` Section 2
- **Node signature validation:** Verify LangGraph nodes match `specs/technical.md` Section 3.1
- **HITL threshold validation:** Ensure confidence thresholds are exactly 0.90/0.70 (non-negotiable)
- **Model selection validation:** Verify agents use correct LLM models from `specs/technical.md` Section 6.1

**MCP Primitives:**

**Tools:**
- `validate_schema` - Validate Pydantic schema against spec
  - **Parameters:** `{schema_name: str, schema_code: str, spec_section: str}`
  - **Returns:** `{valid: bool, errors: list[ValidationError], warnings: list[str]}`
  - **Example:** Validate `GlobalState` matches `specs/technical.md` Section 2.1

- `validate_node_signature` - Validate LangGraph node signature
  - **Parameters:** `{node_name: str, function_signature: str, spec_section: str}`
  - **Returns:** `{valid: bool, errors: list[str]}`
  - **Example:** Verify `planner_node(state: GlobalState) -> GlobalState`

- `check_hitl_thresholds` - Verify HITL thresholds are correct
  - **Parameters:** `{code_snippet: str}`
  - **Returns:** `{valid: bool, found_thresholds: dict, expected_thresholds: dict}`
  - **Example:** Ensure code uses 0.90/0.70, not 0.85/0.75

- `generate_traceability_matrix` - Generate code-to-spec mapping
  - **Parameters:** `{directory: str}`
  - **Returns:** `{matrix: list[TraceabilityEntry]}`
  - **Example:** Map all Python files to spec sections

**Resources:**
- `specs://schemas` - List all Pydantic schemas from specs
- `specs://nodes` - List all LangGraph nodes from specs
- `specs://constraints` - List all non-negotiable constraints (HITL thresholds, model selection)

**Prompts:**
- `validate_implementation` - Prompt template for validating code against specs

**Usage Example (Developer Workflow):**
```
1. Developer writes GlobalState schema in src/chimera/state/schemas.py
2. Developer calls MCP tool: validate_schema("GlobalState", <code>, "specs/technical.md#2.1")
3. MCP returns: {valid: false, errors: ["Missing field 'version'", "Field 'goal' max_length should be 500, found 1000"]}
4. Developer fixes code
5. Developer re-validates until valid: true
6. Developer commits
```

**Spec References:**
- `.cursor/rules` Section 2 (Prime Directive: Spec-First Development)
- `.cursor/rules` Section 6 (Implementation Constraints)

---

### 2.3 State Inspector MCP (Proposed)

**Status:** 🔮 Proposed for Future Implementation

**Name:** `chimera-state-inspector`

**Purpose:**
Inspect LangGraph state during development and debugging. Provides structured access to `GlobalState` at any point in the agent workflow, enabling developers to understand state transitions and debug issues.

**Why MCP (Not a Skill):**
- **Developer-facing:** Used for debugging, not by agents at runtime
- **Observability:** Provides read-only access to runtime state
- **IDE integration:** Developers can query state from Cursor/VS Code
- **Standardized interface:** MCP provides structured state representation

**How It Supports Traceability:**
- Links state transitions to Tenx Sense logs
- Shows which agent action caused which state change
- Provides audit trail: Initial state → Planner → Worker → Judge → Final state
- Includes `trace_id` for every state transition

**How It Supports SDD:**
- Validates that state transitions match `specs/technical.md` Section 3.2 (Edge Conditions)
- Verifies that `GlobalState` schema matches `specs/technical.md` Section 2.1
- Confirms that state updates follow immutability patterns (new state returned, not mutated)
- Detects spec violations: e.g., `status` field has invalid value not in Literal

**MCP Primitives:**

**Tools:**
- `get_current_state` - Get current GlobalState for a session
  - **Parameters:** `{session_id: str}`
  - **Returns:** `{state: GlobalState, last_updated: str, current_node: str}`
  - **Example:** Inspect state after Planner completes

- `list_state_history` - Get state transition history
  - **Parameters:** `{session_id: str, limit: int = 50}`
  - **Returns:** `{history: list[StateSnapshot]}`
  - **Example:** See how state evolved from planning → executing → reviewing

- `validate_state_transition` - Validate state transition against specs
  - **Parameters:** `{from_state: GlobalState, to_state: GlobalState, node_name: str}`
  - **Returns:** `{valid: bool, violations: list[str]}`
  - **Example:** Verify Planner correctly updated `task_queue` and `status`

- `diff_states` - Compare two states
  - **Parameters:** `{state_a: GlobalState, state_b: GlobalState}`
  - **Returns:** `{differences: list[StateDiff]}`
  - **Example:** See what changed between two checkpoints

**Resources:**
- `state://current/{session_id}` - Current state for session
- `state://history/{session_id}` - State transition history
- `state://checkpoints/{session_id}` - LangGraph checkpoints (for HITL resume)

**Prompts:**
- `debug_state_transition` - Prompt template for debugging state issues

**Usage Example (Debugging Workflow):**
```
1. Developer runs agent workflow, it fails at Worker node
2. Developer calls: get_current_state(session_id="abc123")
3. MCP returns: {state: {...}, current_node: "worker", status: "executing"}
4. Developer calls: list_state_history(session_id="abc123")
5. MCP returns: [
     {node: "planner", status: "planning", task_queue: [...]},
     {node: "worker", status: "executing", task_queue: [...], error: "MCP timeout"}
   ]
6. Developer identifies issue: Worker task timeout too short
7. Developer checks specs/technical.md Section 2.2: timeout default is 60s
8. Developer finds bug: Code uses 30s instead of 60s
9. Developer fixes code to match spec
```

**Spec References:**
- `specs/technical.md` Section 2.1 (GlobalState schema)
- `specs/technical.md` Section 3.2 (Edge Conditions)
- `specs/technical.md` Section 3.3 (HITL Interrupts - checkpointer)

---

### 2.4 Redis Queue Monitor MCP (Proposed)

**Status:** 🔮 Proposed for Future Implementation

**Name:** `chimera-redis-monitor`

**Purpose:**
Monitor Redis task queues and dead letter queues (DLQ) during development and production. Provides visibility into queue depth, task processing rates, and failed tasks.

**Why MCP (Not a Skill):**
- **Developer-facing:** Used for monitoring and debugging, not by agents
- **Observability:** Provides read-only access to queue state
- **Operational tool:** Supports both development and production monitoring
- **Standardized interface:** MCP provides structured queue inspection

**How It Supports Traceability:**
- Links queued tasks to Tenx Sense logs
- Shows which tasks are pending, processing, or failed
- Provides audit trail for task lifecycle: Queued → Processing → Complete/Failed
- Enables debugging: "Why is this task stuck in the queue?"

**How It Supports SDD:**
- Validates that queue behavior matches `specs/technical.md` Section 4 (Redis Queue Contracts)
- Verifies queue naming conventions: `chimera:tasks:{session_id}`, `chimera:dlq:{session_id}`
- Confirms TTL policies are applied correctly (24 hours for completed tasks)
- Detects spec violations: e.g., tasks in DLQ without error messages

**MCP Primitives:**

**Tools:**
- `list_queues` - List all active task queues
  - **Parameters:** `{pattern: str = "chimera:tasks:*"}`
  - **Returns:** `{queues: list[QueueInfo]}`
  - **Example:** See all active sessions with pending tasks

- `inspect_queue` - Inspect specific queue
  - **Parameters:** `{queue_name: str, limit: int = 10}`
  - **Returns:** `{depth: int, tasks: list[Task], oldest_task_age: int}`
  - **Example:** See what tasks are pending for session "abc123"

- `drain_dlq` - Retrieve failed tasks from dead letter queue
  - **Parameters:** `{session_id: str, limit: int = 100}`
  - **Returns:** `{failed_tasks: list[Task], error_summary: dict}`
  - **Example:** Debug why tasks are failing

- `get_queue_metrics` - Get queue performance metrics
  - **Parameters:** `{session_id: str}`
  - **Returns:** `{tasks_queued: int, tasks_completed: int, tasks_failed: int, avg_processing_time: float}`
  - **Example:** Monitor queue throughput

**Resources:**
- `redis://queues` - List all queues
- `redis://queue/{session_id}` - Specific queue details
- `redis://dlq/{session_id}` - Dead letter queue for session
- `redis://metrics` - Aggregate queue metrics

**Prompts:**
- `diagnose_queue_issue` - Prompt template for debugging queue problems

**Usage Example (Monitoring Workflow):**
```
1. Developer notices agent workflow is slow
2. Developer calls: list_queues()
3. MCP returns: [{queue: "chimera:tasks:abc123", depth: 47, oldest_task_age: 3600}]
4. Developer sees queue has 47 pending tasks, oldest is 1 hour old
5. Developer calls: inspect_queue("chimera:tasks:abc123", limit=5)
6. MCP returns: [{task_id: "xyz", type: "mcp_call", mcp_tool: "twitter_trends", timeout: 30}, ...]
7. Developer identifies issue: All tasks are waiting for Twitter API (rate limited)
8. Developer calls: drain_dlq("abc123")
9. MCP returns: {failed_tasks: [...], error_summary: {"RateLimitError": 12, "TimeoutError": 3}}
10. Developer adjusts retry policy in specs/technical.md Section 5.4
```

**Spec References:**
- `specs/technical.md` Section 4 (Redis Queue Contracts)
- `specs/functional.md` Section 2.2 (Worker Agent - Retry/Timeout Policies)

---

## 3. Why These Are MCP (Not Skills)

### 3.1 Decision Criteria

| Criterion | Developer MCP Tools | Runtime Agent Skills |
|-----------|---------------------|----------------------|
| **Primary User** | Human developers, AI coding assistants | Autonomous agents (Planner, Worker, Judge) |
| **Execution Context** | Development, debugging, monitoring | Production agent workflows |
| **Lifecycle** | Long-running services (IDE integration) | Function calls during task execution |
| **State** | Read-only observability | Read-write task execution |
| **Examples** | Spec validator, state inspector, queue monitor | Trend analysis, content generation |

### 3.2 Why Tenx Sense Is MCP

**Tenx MCP Sense is both a Developer Tool AND a Runtime Tool:**
- **Developer use:** Query logs during debugging, validate traceability
- **Runtime use:** Agents log actions during execution

**Why MCP (not a Skill):**
- **External service:** Hosted by 10Academy, not part of Chimera codebase
- **Standardized protocol:** Uses MCP for logging and querying
- **Observability:** Provides structured access to agent action history
- **Required by SRS:** FR 4.0 mandates MCP Sense integration

### 3.3 Why Spec Validator Is MCP

**Why not a Python script?**
- **IDE integration:** MCP enables real-time validation in Cursor/VS Code
- **Standardized interface:** MCP provides structured validation results
- **Reusability:** Other projects can use the same validator
- **Separation of concerns:** Validation logic separate from agent logic

**Why not a Skill?**
- **Not used by agents:** Agents don't validate their own code
- **Developer-facing:** Used during development, not runtime
- **No task execution:** Doesn't execute agent tasks, only validates code

### 3.4 Why State Inspector Is MCP

**Why not a debugging library?**
- **Structured access:** MCP provides standardized state representation
- **IDE integration:** Developers can query state from Cursor/VS Code
- **Traceability:** Links state transitions to Tenx Sense logs

**Why not a Skill?**
- **Read-only:** Doesn't modify state, only inspects it
- **Developer-facing:** Used for debugging, not by agents
- **Observability:** Provides visibility, not execution

### 3.5 Why Redis Monitor Is MCP

**Why not Redis CLI?**
- **Structured interface:** MCP provides typed queue inspection
- **Traceability:** Links queued tasks to Tenx Sense logs
- **Chimera-specific:** Understands Chimera queue naming conventions

**Why not a Skill?**
- **Operational tool:** Used for monitoring, not task execution
- **Read-only:** Doesn't process tasks, only inspects queues
- **Developer-facing:** Used for debugging and monitoring

---

## 4. Integration with SDD Workflow

### 4.1 Spec-Driven Development Workflow (with MCP Tools)

**Step 1: Read Specs**
- Developer reads `specs/functional.md` and `specs/technical.md`
- Identifies what needs to be implemented

**Step 2: Implement Code**
- Developer writes Pydantic schemas, LangGraph nodes, etc.
- Follows specs exactly (no additions, no deviations)

**Step 3: Validate with Spec Validator MCP**
- Developer calls `validate_schema()` to check Pydantic schemas
- Developer calls `validate_node_signature()` to check LangGraph nodes
- Developer calls `check_hitl_thresholds()` to verify HITL logic
- **If validation fails:** Fix code to match specs

**Step 4: Test with State Inspector MCP**
- Developer runs agent workflow in test mode
- Developer calls `get_current_state()` to inspect state at each node
- Developer calls `validate_state_transition()` to verify state updates
- **If state transitions are wrong:** Fix code to match specs

**Step 5: Verify Traceability with Tenx Sense MCP**
- Developer calls `tenx_query_sessions()` to see logged actions
- Developer verifies all agent actions are logged
- Developer checks that `trace_id` is present in all logs
- **If traceability is missing:** Add logging to match specs

**Step 6: Monitor with Redis Monitor MCP**
- Developer calls `list_queues()` to see active queues
- Developer calls `inspect_queue()` to verify task processing
- Developer calls `drain_dlq()` to debug failed tasks
- **If queue behavior is wrong:** Fix code to match specs

**Step 7: Commit with Spec References**
- Developer commits code with conventional commit message
- Commit message references spec sections (e.g., "specs/technical.md §2.1")
- Git history shows traceability: Code → Spec → SRS

### 4.2 Example: Implementing GlobalState Schema

**Without MCP Tools (Error-Prone):**
```
1. Developer reads specs/technical.md Section 2.1
2. Developer writes GlobalState schema
3. Developer commits code
4. Later: Bug discovered - missing 'version' field
5. Fix requires code change + test update
```

**With MCP Tools (Validated):**
```
1. Developer reads specs/technical.md Section 2.1
2. Developer writes GlobalState schema
3. Developer calls: validate_schema("GlobalState", <code>, "specs/technical.md#2.1")
4. MCP returns: {valid: false, errors: ["Missing field 'version'"]}
5. Developer adds 'version' field
6. Developer re-validates: {valid: true}
7. Developer commits code (validated against spec)
```

**Result:** Spec compliance enforced at development time, not discovered in production.

---

## 5. Future Developer Tools (Out of Scope for Phase 1)

### 5.1 LLM Cost Tracker MCP
- **Purpose:** Track LLM token usage and costs per session
- **Tools:** `get_session_cost()`, `get_model_usage()`, `estimate_cost()`
- **Resources:** `costs://session/{id}`, `costs://daily`, `costs://by_model`
- **Why:** Optimize LLM usage, stay within budget constraints

### 5.2 HITL Review Dashboard MCP
- **Purpose:** Provide UI for human reviewers to approve/reject tasks
- **Tools:** `list_pending_reviews()`, `approve_task()`, `reject_task()`
- **Resources:** `reviews://pending`, `reviews://history/{session_id}`
- **Why:** Enable human-in-the-loop workflow (specs/functional.md Section 3)

### 5.3 Agent Performance Profiler MCP
- **Purpose:** Profile agent performance (execution time, bottlenecks)
- **Tools:** `profile_session()`, `get_bottlenecks()`, `compare_sessions()`
- **Resources:** `profiling://session/{id}`, `profiling://summary`
- **Why:** Optimize agent performance, identify slow nodes

### 5.4 Spec Diff Tracker MCP
- **Purpose:** Track spec changes over time, show impact on code
- **Tools:** `diff_specs()`, `find_affected_code()`, `generate_migration_plan()`
- **Resources:** `specs://versions`, `specs://diff/{v1}/{v2}`
- **Why:** Manage spec evolution, ensure code stays in sync

### 5.5 A2A Protocol Inspector MCP (Month 2+)
- **Purpose:** Inspect Agent-to-Agent communication (when A2A is implemented)
- **Tools:** `list_agent_connections()`, `inspect_a2a_message()`, `validate_a2a_protocol()`
- **Resources:** `a2a://connections`, `a2a://messages/{agent_id}`
- **Why:** Debug inter-agent communication (out of scope for Phase 1 per ADR-005)

---

## 6. Summary

### 6.1 Developer MCP Tools for Phase 1

| Tool | Status | Purpose | Key Benefit |
|------|--------|---------|-------------|
| **Tenx MCP Sense** | ✅ Configured | Traceability & logging | Required by FR 4.0, enables audit trail |
| **Spec Validator MCP** | 🔮 Proposed | Validate code against specs | Enforces SDD at development time |
| **State Inspector MCP** | 🔮 Proposed | Inspect LangGraph state | Debug state transitions, verify spec compliance |
| **Redis Monitor MCP** | 🔮 Proposed | Monitor task queues | Operational visibility, debug queue issues |

### 6.2 Key Takeaways

1. **MCP for Developer Tools:** Standardized interface for IDE integration, observability, and validation
2. **Traceability First:** All tools link back to Tenx Sense for end-to-end tracing
3. **Spec Compliance:** Tools enforce specs at development time, not runtime
4. **Separation of Concerns:** Developer tools ≠ Runtime tools ≠ Agent skills

### 6.3 Alignment with Specs

- **ADR-005:** MCP for tool/data access (not agent-to-agent communication)
- **FR 4.0:** Tenx MCP Sense mandatory for traceability
- **SDD Governance:** `.cursor/rules` Section 2 (Prime Directive: Spec-First Development)
- **Implementation Constraints:** `.cursor/rules` Section 6 (Pydantic, LangGraph, MCP, LLM)

---

**END OF TOOLING STRATEGY DOCUMENT**

**Next Steps:**
1. Implement Tenx MCP Sense integration (already configured)
2. Propose Spec Validator MCP for future implementation
3. Define Runtime Agent Skills in `skills/README.md`
4. Implement agent nodes that use these tools

**References:**
- `specs/technical.md` Section 5 (MCP Server Configuration)
- `specs/functional.md` Section 4 (MCP Integration Requirements)
- `.cursor/rules` Section 2 (Prime Directive: Spec-First Development)
- `.vscode/mcp.json` (Tenx Sense configuration)


