# Project Chimera: Technical Specification

**Version:** 0.1.0  
**Status:** Draft  
**SRS Reference:** Project Chimera SRS Document (Autonomous Influencer Network)  
**Last Updated:** 2026-02-06

---

## 1. Architecture Overview

### 1.1 Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                      LangGraph StateGraph                    │
│                                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Planner  │─────▶│  Worker  │─────▶│  Judge   │          │
│  │  Node    │      │   Node   │      │   Node   │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│       │                  │                  │               │
│       │                  │                  ▼               │
│       │                  │         ┌─────────────────┐     │
│       │                  │         │ HITL Interrupt  │     │
│       │                  │         │  (confidence    │     │
│       │                  │         │   0.70-0.90)    │     │
│       │                  │         └─────────────────┘     │
│       │                  │                                  │
│       ▼                  ▼                                  │
│  ┌──────────────────────────────────────────┐              │
│  │         GlobalState (Pydantic)           │              │
│  │  - session_id, goal, task_queue          │              │
│  │  - completed_tasks, pending_reviews      │              │
│  └──────────────────────────────────────────┘              │
│                       │                                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Redis (State +  │
              │   Task Queues)   │
              └──────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   MCP Servers    │
              │  - Tenx Sense    │
              │  - Platform APIs │
              └──────────────────┘
```

### 1.2 Data Flow Diagram
```
1. User submits goal → GlobalState created
2. Planner reads GlobalState → produces TaskQueue
3. Worker pops Task from queue → executes via MCP → produces WorkerResult
4. Judge reads WorkerResult → calculates confidence → produces ReviewDecision
5. If confidence 0.70-0.90 → HITL interrupt → await human approval
6. If approved/auto-approved → mark complete → next task
7. Repeat 3-6 until queue empty
8. GlobalState.status = "complete"
```

### 1.3 Deployment Model (Phase 1)
- **Single process:** All agents run in one Python process
- **Local Redis:** Single Redis instance (no cluster)
- **No load balancer:** Direct API access
- **No containerization yet:** Native Python execution (Docker on Day 3)

---

## 2. Pydantic Schemas (Executable Contracts)

### 2.1 GlobalState
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Any

class GlobalState(BaseModel):
    """Root state object for entire agent workflow."""
    
    session_id: str = Field(..., description="Unique session identifier")
    goal: str = Field(..., min_length=10, max_length=500, description="High-level objective")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    constraints: list[str] = Field(default_factory=list, description="Business rules")
    
    # Task management
    task_queue: list["Task"] = Field(default_factory=list)
    completed_tasks: list["WorkerResult"] = Field(default_factory=list)
    pending_reviews: list["ReviewItem"] = Field(default_factory=list)
    
    # Status tracking
    status: Literal["planning", "executing", "reviewing", "complete", "failed"] = "planning"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    version: int = Field(default=1, description="For optimistic concurrency control")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "goal": "Research trending AI topics on Twitter",
                "context": {"platform": "twitter", "timeframe": "24h"},
                "constraints": ["no political content", "english only"],
                "status": "planning"
            }
        }
```

**Validation Rules:**
- `goal` must be 10-500 characters
- `session_id` must be unique (enforced at application layer)
- `status` transitions must follow: planning → executing → reviewing → complete/failed
- `version` increments on every update (OCC)

---

### 2.2 Task
```python
class Task(BaseModel):
    """Individual unit of work for Worker agent."""
    
    id: str = Field(..., description="Unique task ID (UUID)")
    type: Literal["mcp_call", "computation", "validation"] = Field(...)
    description: str = Field(..., min_length=5, max_length=200)
    
    # MCP-specific fields
    mcp_tool: str | None = Field(None, description="MCP tool name (e.g., 'tenx_sense_log')")
    parameters: dict[str, Any] = Field(default_factory=dict)
    
    # Execution control
    timeout: int = Field(default=60, ge=5, le=300, description="Timeout in seconds")
    retry_count: int = Field(default=0, ge=0, le=3)
    
    # Dependencies
    depends_on: list[str] = Field(default_factory=list, description="Task IDs that must complete first")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "task_xyz789",
                "type": "mcp_call",
                "description": "Fetch trending topics from Twitter API",
                "mcp_tool": "twitter_trends",
                "parameters": {"location": "US", "limit": 10},
                "timeout": 30
            }
        }
```

**Validation Rules:**
- `timeout` must be 5-300 seconds
- `retry_count` must be 0-3
- If `type == "mcp_call"`, `mcp_tool` must not be None
- `depends_on` must not create circular dependencies (validated at runtime)

---

### 2.3 WorkerResult
```python
class WorkerResult(BaseModel):
    """Output from Worker agent after task execution."""
    
    task_id: str = Field(..., description="Reference to Task.id")
    status: Literal["success", "failure", "timeout"] = Field(...)
    
    # Success path
    output: Any | None = Field(None, description="Task result (if success)")
    
    # Failure path
    error: str | None = Field(None, description="Error message (if failure/timeout)")
    error_type: str | None = Field(None, description="Error classification")
    
    # Metadata
    execution_time: float = Field(..., ge=0, description="Execution time in seconds")
    mcp_trace: dict[str, Any] | None = Field(None, description="MCP call metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_xyz789",
                "status": "success",
                "output": {"trends": ["AI agents", "LangGraph", "MCP"]},
                "execution_time": 2.34,
                "mcp_trace": {"server": "tenx_sense", "call_id": "call_123"}
            }
        }
```

**Validation Rules:**
- If `status == "success"`, `output` must not be None
- If `status == "failure"` or `status == "timeout"`, `error` must not be None
- `execution_time` must be non-negative

---

### 2.4 ReviewDecision
```python
class ReviewDecision(BaseModel):
    """Output from Judge agent after evaluating WorkerResult."""
    
    task_id: str = Field(..., description="Reference to Task.id")
    approved: bool = Field(..., description="Auto-approved (True) or auto-rejected (False)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    requires_human_review: bool = Field(..., description="HITL trigger")
    
    # Explanation
    reasoning: str = Field(..., min_length=10, description="Judge's rationale")
    quality_metrics: dict[str, float] = Field(default_factory=dict, description="Scoring breakdown")
    
    # Human reviewer guidance
    suggested_action: str | None = Field(None, description="Recommendation for reviewer")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_xyz789",
                "approved": False,
                "confidence": 0.75,
                "requires_human_review": True,
                "reasoning": "Output format is correct but content quality is uncertain",
                "quality_metrics": {"format": 1.0, "completeness": 0.8, "relevance": 0.6},
                "suggested_action": "Verify that trends are actually trending in the last 24h"
            }
        }
```

**Validation Rules:**
- `confidence` must be 0.0-1.0
- If `confidence > 0.90`, `approved` must be True and `requires_human_review` must be False
- If `0.70 <= confidence <= 0.90`, `requires_human_review` must be True
- If `confidence < 0.70`, `approved` must be False and `requires_human_review` must be False
- `reasoning` must be at least 10 characters

---

### 2.5 ReviewItem
```python
class ReviewItem(BaseModel):
    """Item in the ReviewQueue awaiting human approval."""
    
    review_id: str = Field(..., description="Unique review ID (UUID)")
    task_id: str = Field(..., description="Reference to Task.id")
    
    worker_result: WorkerResult
    judge_decision: ReviewDecision
    
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    timeout_at: datetime = Field(..., description="Auto-reject after this time")
    
    status: Literal["pending", "approved", "rejected", "timeout"] = Field(default="pending")
    reviewer_notes: str | None = Field(None, description="Human reviewer comments")
    
    class Config:
        json_schema_extra = {
            "example": {
                "review_id": "rev_abc123",
                "task_id": "task_xyz789",
                "status": "pending",
                "timeout_at": "2026-02-07T19:41:00Z"
            }
        }
```

**Validation Rules:**
- `timeout_at` must be after `submitted_at`
- `status` can only transition: pending → approved/rejected/timeout
- Once status is approved/rejected/timeout, it cannot change

---

## 3. LangGraph State Machine

### 3.1 Node Definitions

**Planner Node:**
```python
def planner_node(state: GlobalState) -> GlobalState:
    """
    Reads state.goal and state.context.
    Calls LLM to generate task list.
    Updates state.task_queue.
    Returns updated state.
    """
```

**Worker Node:**
```python
def worker_node(state: GlobalState) -> GlobalState:
    """
    Pops next task from state.task_queue.
    Executes task (MCP call or computation).
    Appends WorkerResult to state.completed_tasks.
    Returns updated state.
    """
```

**Judge Node:**
```python
def judge_node(state: GlobalState) -> GlobalState:
    """
    Reads last WorkerResult from state.completed_tasks.
    Evaluates quality and calculates confidence.
    If requires_human_review, adds to state.pending_reviews.
    Returns updated state.
    """
```

---

### 3.2 Edge Conditions

**should_continue_planning:**
```python
def should_continue_planning(state: GlobalState) -> str:
    """
    After planner_node.
    Returns "worker" if task_queue is not empty.
    Returns "end" if task_queue is empty (planning failed).
    """
```

**should_request_approval:**
```python
def should_request_approval(state: GlobalState) -> str:
    """
    After judge_node.
    Returns "hitl_interrupt" if last ReviewDecision.requires_human_review == True.
    Returns "worker" if more tasks in queue and approved.
    Returns "end" if queue empty.
    """
```

**should_retry:**
```python
def should_retry(state: GlobalState) -> str:
    """
    After worker_node if task failed.
    Returns "worker" if task.retry_count < 3.
    Returns "judge" if retry limit reached.
    """
```

---

### 3.3 HITL Interrupt Points

**Interrupt Configuration:**
```python
from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph

graph = StateGraph(GlobalState)
graph.add_node("planner", planner_node)
graph.add_node("worker", worker_node)
graph.add_node("judge", judge_node)

# Interrupt before continuing after judge
graph.add_conditional_edges(
    "judge",
    should_request_approval,
    {
        "hitl_interrupt": "human_review",  # Pause here
        "worker": "worker",
        "end": END
    }
)

# Compile with checkpointer for state persistence
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer, interrupt_before=["human_review"])
```

**Resume After Approval:**
```python
# Human approves via API
app.update_state(config={"configurable": {"thread_id": session_id}}, values={"status": "executing"})
app.invoke(None, config={"configurable": {"thread_id": session_id}})  # Resume
```

---

### 3.4 Error Recovery Paths

**Worker Failure:**
```
worker_node (failure) → should_retry → worker_node (retry) → judge_node
```

**Judge Rejection:**
```
judge_node (confidence < 0.70) → mark task failed → continue to next task
```

**HITL Timeout:**
```
human_review (24h timeout) → auto-reject → mark task failed → continue
```

---

## 4. Redis Queue Contracts

### 4.1 Queue Naming Conventions
- **Task queue:** `chimera:tasks:{session_id}`
- **Review queue:** `chimera:reviews:pending`
- **State snapshots:** `chimera:state:{session_id}`
- **Dead letter queue:** `chimera:dlq:{session_id}`

### 4.2 Message Format (JSON Schema)
```python
# Task queue message
{
    "task_id": "task_xyz789",
    "session_id": "sess_abc123",
    "task": {/* Task schema */},
    "enqueued_at": "2026-02-06T19:41:00Z"
}

# Review queue message
{
    "review_id": "rev_abc123",
    "session_id": "sess_abc123",
    "review_item": {/* ReviewItem schema */},
    "enqueued_at": "2026-02-06T19:41:00Z"
}
```

### 4.3 TTL Policies
- **Task messages:** 24 hours (expire if not processed)
- **Review messages:** 48 hours (expire after timeout + grace period)
- **State snapshots:** 7 days (for debugging)
- **Dead letter messages:** 30 days (for analysis)

### 4.4 Dead Letter Queue Handling
- Failed tasks after 3 retries → move to DLQ
- DLQ messages include full error trace
- Manual intervention required to reprocess

**Redis Commands:**
```python
# Enqueue task
redis.lpush(f"chimera:tasks:{session_id}", json.dumps(task_message))

# Dequeue task (blocking)
task_json = redis.brpop(f"chimera:tasks:{session_id}", timeout=5)

# Move to DLQ
redis.lpush(f"chimera:dlq:{session_id}", json.dumps(failed_task))
```

---

## 5. MCP Server Configuration

### 5.1 Tenx Sense Connection

**Configuration (from .vscode/mcp.json):**
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

**Python Client:**
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_tenx_sense():
    server_params = StdioServerParameters(
        command="uvx",
        args=["mcp-server-fetch"],
        env={
            "TENX_MCP_URL": os.getenv("TENX_MCP_URL"),
            "TENX_API_KEY": os.getenv("TENX_API_KEY")
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Use session for MCP calls
```

### 5.2 Required MCP Primitives

**Resources:**
- `tenx://feedback/sessions` - List all sessions
- `tenx://feedback/session/{id}` - Get session details

**Tools:**
- `tenx_log_action` - Log agent action
  - Parameters: `{session_id, action_type, metadata}`
  - Returns: `{logged: bool, trace_id: str}`

**Prompts:**
- None required for Phase 1

### 5.3 Authentication Flow
1. Load `TENX_API_KEY` from environment
2. Pass as env var to MCP server process
3. MCP server handles authentication with Tenx backend
4. Client receives authenticated session

### 5.4 Rate Limiting
- **Tenx Sense:** 100 requests/minute (assumed)
- **Strategy:** Exponential backoff on 429 errors
- **Fallback:** Queue logs locally, batch upload

---

## 6. LLM Provider Configuration

### 6.1 Model Selection Matrix

| Agent   | Model                     | Rationale                          | Cost/1M tokens |
|---------|---------------------------|------------------------------------|----------------|
| Planner | claude-3-5-sonnet-20241022| Complex reasoning, planning        | $3.00 / $15.00 |
| Worker  | gemini-2.0-flash-exp      | Fast execution, low cost           | Free (preview) |
| Judge   | claude-3-5-sonnet-20241022| Quality evaluation, consistency    | $3.00 / $15.00 |

**Fallback Strategy:**
- If primary model fails → retry with same model once
- If retry fails → use `gpt-4o-mini` as fallback
- If fallback fails → mark task as failed

### 6.2 Prompt Templates

**Planner System Prompt:**
```
You are a task planning agent. Given a high-level goal, decompose it into 3-10 atomic subtasks.

Rules:
- Each task must be executable by a single MCP tool call or simple computation
- Tasks must be ordered by dependency (no circular dependencies)
- Each task must have clear success criteria
- Output valid JSON matching the TaskQueue schema

Goal: {goal}
Context: {context}
Constraints: {constraints}

Output format:
{
  "tasks": [...],
  "reasoning": "...",
  "estimated_duration": 30
}
```

**Worker System Prompt:**
```
You are a task execution agent. Execute the given task using the specified MCP tool.

Task: {task.description}
MCP Tool: {task.mcp_tool}
Parameters: {task.parameters}

Execute the task and return the result in JSON format matching the WorkerResult schema.
```

**Judge System Prompt:**
```
You are a quality control agent. Evaluate the Worker's output and assign a confidence score (0.0-1.0).

Scoring criteria:
- Format correctness (0.3 weight)
- Completeness (0.3 weight)
- Relevance to task (0.4 weight)

Worker Result: {worker_result}

Output format:
{
  "approved": true/false,
  "confidence": 0.85,
  "requires_human_review": false,
  "reasoning": "...",
  "quality_metrics": {"format": 1.0, "completeness": 0.9, "relevance": 0.7}
}
```

### 6.3 Token Budget Constraints
- **Planner:** Max 4000 input tokens, 1000 output tokens
- **Worker:** Max 2000 input tokens, 500 output tokens
- **Judge:** Max 3000 input tokens, 500 output tokens

**Enforcement:**
```python
from litellm import completion

response = completion(
    model="claude-3-5-sonnet-20241022",
    messages=[...],
    max_tokens=1000,
    temperature=0.7
)
```

### 6.4 Fallback Strategies
- Primary fails → Retry once with same model
- Retry fails → Switch to fallback model (gpt-4o-mini)
- Fallback fails → Return error to user

---

## 7. API Contracts (FastAPI)

### 7.1 POST /tasks - Submit New Task
**Request:**
```json
{
  "goal": "Research trending AI topics on Twitter",
  "context": {"platform": "twitter", "timeframe": "24h"},
  "constraints": ["no political content", "english only"]
}
```

**Response (202 Accepted):**
```json
{
  "session_id": "sess_abc123",
  "status": "planning",
  "created_at": "2026-02-06T19:41:00Z"
}
```

### 7.2 GET /tasks/{session_id} - Status Check
**Response (200 OK):**
```json
{
  "session_id": "sess_abc123",
  "status": "executing",
  "progress": {
    "total_tasks": 5,
    "completed_tasks": 2,
    "pending_reviews": 1
  },
  "updated_at": "2026-02-06T19:45:00Z"
}
```

### 7.3 POST /reviews/{review_id}/approve - HITL Approval
**Request:**
```json
{
  "reviewer_notes": "Verified trends are accurate"
}
```

**Response (200 OK):**
```json
{
  "review_id": "rev_abc123",
  "status": "approved",
  "resumed": true
}
```

### 7.4 GET /state/{session_id} - Global State Inspection
**Response (200 OK):**
```json
{
  "session_id": "sess_abc123",
  "goal": "Research trending AI topics on Twitter",
  "status": "executing",
  "task_queue": [...],
  "completed_tasks": [...],
  "pending_reviews": [...]
}
```

---

## 8. Environment Configuration

### 8.1 Required Variables (from .env.example)
```bash
# MCP Sense
TENX_MCP_URL=https://mcppulse.10academy.org/proxy
TENX_API_KEY=<secret>

# LLM Providers
ANTHROPIC_API_KEY=<secret>
OPENAI_API_KEY=<secret>
GOOGLE_API_KEY=<secret>

# Infrastructure
REDIS_URL=redis://localhost:6379/0

# Agent Configuration
PLANNER_MODEL=claude-3-5-sonnet-20241022
WORKER_MODEL=gemini-2.0-flash-exp
JUDGE_MODEL=claude-3-5-sonnet-20241022
```

### 8.2 Validation Rules
- All `*_API_KEY` variables must be non-empty
- `REDIS_URL` must be valid Redis connection string
- `*_MODEL` variables must be valid LiteLLM model names

**Validation (Pydantic Settings):**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    tenx_mcp_url: str
    tenx_api_key: str
    anthropic_api_key: str
    redis_url: str
    planner_model: str = "claude-3-5-sonnet-20241022"

    class Config:
        env_file = ".env"
```

### 8.3 Secrets Management
- Never commit `.env` to version control
- Use `.env.example` as template
- In production: Use secret manager (AWS Secrets Manager, etc.)

---

## 9. Testing Contracts

### 9.1 Unit Test Requirements

**Per Component:**
- **Pydantic schemas:** Test validation rules, edge cases
- **LangGraph nodes:** Test with mock state, verify state updates
- **MCP client:** Test with mock MCP server
- **Redis queue:** Test with mock Redis (fakeredis)

**Example:**
```python
def test_global_state_validation():
    # Valid state
    state = GlobalState(session_id="test", goal="Test goal")
    assert state.status == "planning"

    # Invalid goal (too short)
    with pytest.raises(ValidationError):
        GlobalState(session_id="test", goal="Hi")
```

### 9.2 Integration Test Scenarios

**Scenario 1: End-to-End Happy Path**
1. Submit goal via POST /tasks
2. Verify Planner produces tasks
3. Verify Worker executes tasks
4. Verify Judge approves (confidence > 0.90)
5. Verify final status is "complete"

**Scenario 2: HITL Trigger**
1. Submit goal that produces medium-confidence result
2. Verify task enters ReviewQueue
3. Approve via POST /reviews/{id}/approve
4. Verify execution resumes

**Scenario 3: Worker Retry**
1. Mock MCP server to fail once
2. Verify Worker retries
3. Verify success on retry

### 9.3 Mock Strategies for LLM Calls

**Use LiteLLM's mock mode:**
```python
import litellm
litellm.set_verbose = False

def mock_completion(model, messages, **kwargs):
    return {
        "choices": [{
            "message": {
                "content": '{"tasks": [...], "reasoning": "..."}'
            }
        }]
    }

litellm.completion = mock_completion
```

### 9.4 MCP Server Test Doubles

**Use in-memory MCP server:**
```python
class MockMCPServer:
    async def call_tool(self, name, params):
        if name == "tenx_log_action":
            return {"logged": True, "trace_id": "mock_trace"}
        raise ValueError(f"Unknown tool: {name}")
```

---

## 10. Observability

### 10.1 Tenx MCP Sense Integration

**Log Every Agent Action:**
```python
async def log_to_tenx(session_id: str, action_type: str, metadata: dict):
    await mcp_client.call_tool(
        "tenx_log_action",
        {
            "session_id": session_id,
            "action_type": action_type,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**Action Types:**
- `planner_start`, `planner_complete`
- `worker_start`, `worker_complete`, `worker_retry`
- `judge_start`, `judge_complete`
- `hitl_triggered`, `hitl_approved`, `hitl_rejected`

### 10.2 Logging Schema

**Structured Logging (JSON):**
```python
import structlog

logger = structlog.get_logger()
logger.info(
    "worker_task_complete",
    session_id=session_id,
    task_id=task_id,
    status="success",
    execution_time=2.34
)
```

### 10.3 Metrics to Track
- **Latency:** p50, p95, p99 for each agent
- **Success rate:** % of tasks that complete successfully
- **HITL rate:** % of tasks requiring human review
- **Cost:** Total LLM tokens used per session

### 10.4 Tracing Requirements
- Every MCP call must include `trace_id`
- Every LLM call must include `session_id` in metadata
- Every state transition must be logged

---

**End of Technical Specification**

