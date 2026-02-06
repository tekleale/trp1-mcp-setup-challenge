# Agent Nodes

## Overview

This module implements the three core agents in the Planner-Worker-Judge pattern for Project Chimera.

**Architecture Pattern:** FastRender Swarm  
**Spec Reference:** specs/_meta.md ADR-001

---

## Agent Roles and Responsibilities

### 1. Planner Agent

**File:** `planner.py`  
**Class:** `PlannerAgent`  
**Model:** `claude-3-5-sonnet-20241022` (complex reasoning)

**Responsibility:**  
Decompose high-level goals into atomic, executable tasks.

**Key Method:**
- `plan_tasks(goal, context, constraints)` → Task queue

**Inputs:**
- `goal`: High-level objective (string, 10-500 characters)
- `context`: Additional information (dictionary)
- `constraints`: Business rules (list of strings)

**Outputs:**
- `tasks`: List of Task objects (3-10 items)
- `reasoning`: Planning rationale (string)
- `estimated_duration`: Time estimate in minutes (integer)
- `dependency_graph`: Task dependencies (dict)
- `confidence`: Planner confidence score (float, 0.0-1.0)

**Failure Modes:**
- `GoalTooVagueError`: Goal is ambiguous or unclear
- `NoViablePlanError`: Cannot create plan within constraints
- `CircularDependencyError`: Detected circular task dependencies
- `InsufficientCapabilitiesError`: Required skills or tools not available

**Spec References:**
- specs/functional.md Section 2.1 (Planner Agent)
- specs/technical.md Section 3.1 (planner_node)
- specs/technical.md Section 6.2 (Planner System Prompt)

---

### 2. Worker Agent

**File:** `worker.py`  
**Class:** `WorkerAgent`  
**Model:** `gemini-2.0-flash-exp` (fast execution, low cost)

**Responsibility:**  
Execute atomic tasks using MCP tools and internal skills.

**Key Method:**
- `execute_task(task, mcp_server)` → WorkerResult

**Inputs:**
- `task`: Task dictionary with fields:
  - `id`: Unique task ID (string)
  - `type`: Task type ("mcp_call", "computation", "validation")
  - `description`: Human-readable description (string)
  - `mcp_tool`: MCP tool name (string, optional)
  - `parameters`: Tool parameters (dict)
  - `timeout`: Execution timeout in seconds (int, 5-300)
- `mcp_server`: MCP server name (string, optional)

**Outputs:**
- `task_id`: Reference to input task ID (string)
- `status`: Execution status ("success", "failure", "timeout")
- `output`: Task result (any type, if success)
- `error`: Error message (string, if failure/timeout)
- `error_type`: Error classification (string, if failure/timeout)
- `execution_time`: Time taken in seconds (float)
- `mcp_trace`: MCP call metadata (dict, optional)
- `timestamp`: Execution timestamp (datetime)

**Failure Modes:**
- `MCPServerUnavailableError`: Cannot connect to MCP server
- `MCPToolNotFoundError`: Tool does not exist on server
- `MCPAuthenticationError`: Invalid credentials
- `MCPTimeoutError`: Tool execution exceeded timeout
- `MCPRateLimitError`: Rate limit exceeded
- `TaskValidationError`: Invalid task structure

**Retry Policy:**
- Max retries: 3
- Backoff: Exponential (2 seconds base)
- Retry on: timeout, rate_limit, server_unavailable

**Spec References:**
- specs/functional.md Section 2.2 (Worker Agent)
- specs/technical.md Section 2.3 (WorkerResult Schema)
- specs/technical.md Section 3.1 (worker_node)
- specs/technical.md Section 5 (MCP Integration)

---

### 3. Judge Agent

**File:** `judge.py`  
**Class:** `JudgeAgent`  
**Model:** `claude-3-5-sonnet-20241022` (quality evaluation)

**Responsibility:**  
Evaluate Worker outputs and determine if human review is required.

**Key Method:**
- `assess_content(content, guidelines)` → ReviewDecision

**Inputs:**
- `content`: WorkerResult dictionary
- `guidelines`: Quality criteria dictionary with fields:
  - `brand_voice`: Brand voice rules (dict)
  - `format_requirements`: Format specifications (dict)
  - `content_policies`: Content policies (list)

**Outputs:**
- `task_id`: Reference to Task.id (string)
- `approved`: Auto-approved (True) or auto-rejected (False)
- `confidence`: Quality confidence score (float, 0.0-1.0)
- `requires_human_review`: HITL trigger (boolean)
- `reasoning`: Judge's rationale (string, min 10 chars)
- `quality_metrics`: Scoring breakdown (dict[str, float])
- `suggested_action`: Recommendation for reviewer (string, optional)
- `timestamp`: Evaluation timestamp (datetime)

**Failure Modes:**
- `UnsupportedContentTypeError`: Content type not recognized
- `MissingGuidelinesError`: Brand guidelines not provided
- `InvalidContentError`: Content is empty or malformed
- `ScoringError`: Unable to calculate confidence score

**HITL Routing Logic (NON-NEGOTIABLE):**
- **confidence > 0.90:** Auto-approve, no human review
- **0.70 ≤ confidence ≤ 0.90:** Require human review (HITL interrupt)
- **confidence < 0.70:** Auto-reject, no human review

**Quality Scoring Criteria:**
- Format correctness: 0.3 weight
- Completeness: 0.3 weight
- Relevance to task: 0.4 weight

**Spec References:**
- specs/functional.md Section 2.3 (Judge Agent)
- specs/functional.md Section 3.1 (HITL Three-Tier System)
- specs/technical.md Section 2.4 (ReviewDecision Schema)
- specs/technical.md Section 3.1 (judge_node)
- specs/_meta.md Section 3.2 (HITL Thresholds - NON-NEGOTIABLE)

---

## Agent Workflow

```
1. User submits goal → GlobalState created
2. Planner.plan_tasks(goal) → Task queue
3. Worker.execute_task(task) → WorkerResult
4. Judge.assess_content(result) → ReviewDecision
5. If confidence > 0.90: Auto-approve → next task
6. If 0.70 ≤ confidence ≤ 0.90: HITL interrupt → await human approval
7. If confidence < 0.70: Auto-reject → retry or skip
8. Repeat 3-7 until queue empty
9. GlobalState.status = "complete"
```

---

## Implementation Status

**Current:** Skeleton classes with method stubs and comprehensive docstrings  
**Next Steps:**
1. Implement LLM integration (LiteLLM)
2. Implement MCP client integration
3. Implement Skills execution
4. Add Tenx Sense logging
5. Write unit tests for each agent

---

## Testing Requirements

Each agent requires unit tests:
- `tests/agents/test_planner.py`
- `tests/agents/test_worker.py`
- `tests/agents/test_judge.py`

**Spec Reference:** specs/technical.md Section 9 (Testing Contracts)

