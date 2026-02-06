# Project Chimera: Functional Specification

**Version:** 0.1.0  
**Status:** Draft  
**SRS Reference:** Project Chimera SRS Document (Autonomous Influencer Network)  
**Last Updated:** 2026-02-06

---

## 1. System Overview

### 1.1 Mission Statement
Build the foundational infrastructure for autonomous AI influencers—digital entities that research trends, generate content, and manage engagement without human intervention.

**Phase 1 Scope (Day 2-3):** Implement the core Planner-Worker-Judge orchestration pattern with Human-in-the-Loop (HITL) approval gates and MCP integration for external tool access.

### 1.2 Core Capabilities
1. **Task Planning:** Decompose high-level goals into executable subtasks
2. **Task Execution:** Execute subtasks using MCP-connected tools
3. **Quality Control:** Evaluate outputs and route to human review when needed
4. **Human Oversight:** Three-tier approval system based on confidence scores
5. **State Management:** Persistent, traceable state across agent interactions

### 1.3 Out of Scope (Phase 1)
- Agent-to-Agent (A2A) communication
- Multi-agent collaboration
- Production deployment
- UI/UX for human reviewers
- Agentic commerce (crypto wallets)

---

## 2. Agent Roles & Responsibilities

### 2.1 Planner Agent

**SRS Reference:** Section 3.1 (FastRender Swarm - Planner)

**Responsibility:** Decompose high-level goals into actionable subtasks.

**Input Contract:**
```python
class GlobalState(BaseModel):
    goal: str                          # High-level objective
    context: dict[str, Any]            # Additional context
    constraints: list[str]             # Business rules
    max_tasks: int = 10                # Task limit
```

**Output Contract:**
```python
class TaskQueue(BaseModel):
    tasks: list[Task]                  # Ordered list of subtasks
    reasoning: str                     # Planning rationale
    estimated_duration: int            # Minutes
```

**Decision Criteria:**
- Tasks must be atomic (single MCP tool call or simple operation)
- Tasks must be ordered by dependency (no circular dependencies)
- Total tasks ≤ `max_tasks` constraint
- Each task must have clear success criteria

**Failure Modes:**
- **Invalid goal:** Return error if goal is ambiguous or unsafe
- **No viable plan:** Return empty task list with reasoning
- **Timeout:** Return partial plan after 30 seconds

**Success Criteria:**
- 100% of valid goals produce non-empty task lists
- 0% of task lists contain circular dependencies
- 95% of plans complete within estimated duration (±20%)

---

### 2.2 Worker Agent

**SRS Reference:** Section 3.1 (FastRender Swarm - Worker)

**Responsibility:** Execute individual tasks using MCP tools.

**Input Contract:**
```python
class Task(BaseModel):
    id: str                            # Unique task ID
    type: str                          # Task type (mcp_call, computation, etc.)
    description: str                   # Human-readable description
    mcp_tool: str | None               # MCP tool name (if applicable)
    parameters: dict[str, Any]         # Tool parameters
    timeout: int = 60                  # Seconds
```

**Output Contract:**
```python
class WorkerResult(BaseModel):
    task_id: str                       # Reference to input task
    status: Literal["success", "failure", "timeout"]
    output: Any                        # Task result (if success)
    error: str | None                  # Error message (if failure)
    execution_time: float              # Seconds
    mcp_trace: dict | None             # MCP call metadata
```

**MCP Tool Invocation Rules:**
- All MCP calls must use the configured MCP server (Tenx Sense or platform APIs)
- Timeout after `task.timeout` seconds
- Retry once on transient errors (network, rate limit)
- Log all MCP calls to Tenx Sense for traceability

**Retry/Timeout Policies:**
- **Transient errors:** Retry once with exponential backoff (2s, 4s)
- **Permanent errors:** Fail immediately (auth error, invalid parameters)
- **Timeout:** Cancel operation and return timeout status

**Success Criteria:**
- 100% of MCP calls are traced to Tenx Sense
- 95% of tasks complete within timeout
- 0% of tasks fail due to unhandled exceptions

---

### 2.3 Judge Agent

**SRS Reference:** Section 3.1 (FastRender Swarm - Judge), NFR 1.1, NFR 1.2

**Responsibility:** Evaluate Worker outputs and determine if human review is needed.

**Input Contract:**
```python
class WorkerResult(BaseModel):
    # (same as Worker output)
```

**Output Contract:**
```python
class ReviewDecision(BaseModel):
    task_id: str
    approved: bool                     # Auto-approved or rejected
    confidence: float                  # 0.0 to 1.0
    requires_human_review: bool        # HITL trigger
    reasoning: str                     # Explanation
    suggested_action: str | None       # For human reviewer
```

**Confidence Scoring Algorithm:**
- **Input factors:**
  - Task success/failure status
  - Output quality heuristics (length, format, completeness)
  - MCP trace validity
  - Historical success rate for similar tasks
- **Output:** Float between 0.0 (no confidence) and 1.0 (full confidence)
- **Calibration:** Must be tested against human judgments (Day 3)

**HITL Trigger Thresholds (SRS NFR 1.1, NFR 1.2):**
- **confidence > 0.90:** Auto-approve (no human review)
- **0.70 ≤ confidence ≤ 0.90:** Async human review required
- **confidence < 0.70:** Auto-reject (no human review)

**Success Criteria:**
- 100% of decisions include confidence score
- 90% of auto-approved tasks are validated as correct (Day 3 testing)
- 0% of auto-rejected tasks should have been approved (safety)

---

## 3. Human-in-the-Loop (HITL) Workflow

**SRS Reference:** NFR 1.1, NFR 1.2

### 3.1 Three-Tier Approval System

**Tier 1: Auto-Approve (confidence > 0.90)**
- No human intervention
- Task proceeds immediately
- Logged for audit trail

**Tier 2: Async Review (0.70 ≤ confidence ≤ 0.90)**
- Task paused at Judge stage
- Added to ReviewQueue
- Human reviewer notified (future: email/Slack)
- Timeout: 24 hours (configurable)
- Default action on timeout: Reject

**Tier 3: Auto-Reject (confidence < 0.70)**
- No human intervention
- Task marked as failed
- Logged with reasoning

### 3.2 ReviewQueue Schema
```python
class ReviewQueue(BaseModel):
    pending_reviews: list[ReviewItem]
    
class ReviewItem(BaseModel):
    review_id: str
    task_id: str
    worker_result: WorkerResult
    judge_decision: ReviewDecision
    submitted_at: datetime
    timeout_at: datetime
    status: Literal["pending", "approved", "rejected", "timeout"]
```

### 3.3 Approval/Rejection Flows

**Approval Flow:**
1. Human reviewer calls `POST /reviews/{id}/approve`
2. LangGraph resumes from interrupt point
3. Task marked as complete
4. Next task in queue begins

**Rejection Flow:**
1. Human reviewer calls `POST /reviews/{id}/reject` with reason
2. LangGraph marks task as failed
3. Planner may re-plan if configured
4. Audit log updated

### 3.4 Timeout Handling
- After 24 hours (configurable), pending review auto-rejects
- Notification sent to reviewer (future)
- Task marked as `timeout` in audit log

**Success Criteria:**
- 100% of Tier 2 tasks enter ReviewQueue
- 0% of Tier 1/3 tasks enter ReviewQueue
- 100% of timeouts are logged

---

## 4. MCP Integration Requirements

**SRS Reference:** FR 4.0

### 4.1 Required MCP Servers
1. **Tenx MCP Sense** (traceability)
   - URL: `https://mcppulse.10academy.org/proxy`
   - Purpose: Log all agent actions for feedback analytics
   
2. **Platform APIs** (future)
   - Twitter/X API
   - Content generation tools
   - Web search

### 4.2 Resource Access Patterns
- **Read-only resources:** Agent state, historical data
- **Write resources:** Task results, audit logs
- **Transactional:** Must support rollback on failure

### 4.3 Tool Invocation Contracts
```python
class MCPToolCall(BaseModel):
    tool_name: str                     # e.g., "tenx_sense_log"
    parameters: dict[str, Any]
    timeout: int = 30
    retry_policy: RetryPolicy
```

### 4.4 Error Handling
- **Network errors:** Retry with exponential backoff
- **Auth errors:** Fail immediately, alert operator
- **Rate limits:** Queue and retry after delay
- **Invalid parameters:** Fail immediately, log for debugging

**Success Criteria:**
- 100% of MCP calls logged to Tenx Sense
- 95% of transient errors recovered via retry
- 0% of auth errors go unnoticed

---

## 5. State Management

**SRS Reference:** Section 3.2

### 5.1 GlobalState Schema (Pydantic)
```python
class GlobalState(BaseModel):
    session_id: str
    goal: str
    context: dict[str, Any]
    task_queue: TaskQueue
    completed_tasks: list[WorkerResult]
    pending_reviews: list[ReviewItem]
    status: Literal["planning", "executing", "reviewing", "complete", "failed"]
    created_at: datetime
    updated_at: datetime
```

### 5.2 State Transitions
```
planning → executing → reviewing → complete
                    ↓
                  failed
```

### 5.3 Persistence Requirements
- State must survive process restarts
- Use Redis for in-memory state + periodic snapshots
- Checkpoint after each agent action

### 5.4 Concurrency Model (Optimistic Concurrency Control)
- Each state update includes version number
- Concurrent updates detected via version mismatch
- Retry with latest state on conflict

**Success Criteria:**
- 100% of state transitions are valid
- 0% of state lost due to crashes
- 95% of concurrent updates resolve without manual intervention

---

## 6. Success Criteria (Acceptance Tests)

### 6.1 End-to-End Flow
**Given:** A valid goal ("Research trending AI topics")  
**When:** System processes the goal  
**Then:**
- Planner produces 3-5 tasks
- Worker executes all tasks
- Judge evaluates all results
- At least 1 task auto-approves (confidence > 0.90)
- Final state is "complete"

### 6.2 HITL Trigger
**Given:** A task with confidence 0.75  
**When:** Judge evaluates the task  
**Then:**
- Task enters ReviewQueue
- System pauses at interrupt point
- Human approval resumes execution

### 6.3 MCP Traceability
**Given:** Any task execution  
**When:** Worker calls MCP tool  
**Then:**
- Call logged to Tenx Sense
- Trace includes task_id, timestamp, parameters, result

### 6.4 Error Recovery
**Given:** Worker encounters transient error  
**When:** Retry policy executes  
**Then:**
- Task retries once
- Success on retry → task completes
- Failure on retry → task fails with error log

### 6.5 Performance Benchmarks
- **Planner latency:** < 10 seconds for typical goal
- **Worker latency:** < 5 seconds per task (excluding MCP call time)
- **Judge latency:** < 3 seconds per evaluation
- **End-to-end:** < 60 seconds for 5-task workflow (no HITL)

---

**End of Functional Specification**

