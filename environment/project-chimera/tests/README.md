# Test Suite for Project Chimera

## Overview

This directory contains the comprehensive test suite for Project Chimera's agent orchestration system. All tests use pytest with mocks to avoid real network calls, MCP server connections, or LLM API invocations.

**Spec Reference:** specs/technical.md Section 9 (Testing Contracts)

---

## Testing Strategy

### Test Pyramid

```
         /\
        /  \  E2E Tests (Future)
       /____\
      /      \  Integration Tests (Future)
     /________\
    /          \  Unit Tests (Current)
   /____________\
```

**Current Focus:** Unit tests with comprehensive mocking  
**Future:** Integration tests and end-to-end tests

---

## Test Structure

```
tests/
├── agents/                 # Agent node tests
│   ├── test_planner.py    # PlannerAgent tests
│   ├── test_worker.py     # WorkerAgent tests
│   └── test_judge.py      # JudgeAgent tests
├── mcp/                    # MCP integration tests
│   ├── test_mcp_client.py # MCPClient tests
│   └── test_mcp_exceptions.py # Exception tests
├── api/                    # FastAPI endpoint tests
│   ├── test_api_planner.py # Planner API tests
│   ├── test_api_worker.py  # Worker API tests
│   └── test_api_judge.py   # Judge API tests
├── orchestration/          # State machine tests
│   └── test_langgraph_state.py # LangGraph tests
├── governor/               # TDD failing tests (Day 3)
│   ├── test_trend_fetcher.py # Trend fetching TDD goalposts
│   └── test_skills_interface.py # Skills interface TDD goalposts
└── README.md               # This file
```

---

## Test Categories

### 1. Agent Tests (`tests/agents/`)

**Purpose:** Test agent logic without real LLM calls

**Mock Strategy:**
- Mock LiteLLM client responses
- Mock MCP client for Worker agent
- Use fixed confidence scores for Judge agent

**Example:**
```python
@pytest.fixture
def planner_agent():
    with patch('litellm.completion') as mock_llm:
        mock_llm.return_value = {
            "choices": [{"message": {"content": "..."}}]
        }
        return PlannerAgent(model="claude-3-5-sonnet-20241022")
```

**Key Tests:**
- `test_planner.py`: Goal decomposition, dependency validation, duration estimation
- `test_worker.py`: Task execution, retry logic, timeout handling
- `test_judge.py`: Quality assessment, HITL routing (0.90/0.70 thresholds)

---

### 2. MCP Tests (`tests/mcp/`)

**Purpose:** Test MCP client without real network calls

**Mock Strategy:**
- Mock MCP server responses
- Simulate transient errors (timeout, rate limit)
- Simulate permanent errors (auth, tool not found)

**Example:**
```python
@pytest.fixture
def mock_mcp_server():
    server = Mock()
    server.call_tool = AsyncMock(return_value={
        "result": {"logged": True},
        "trace_id": "trace_123"
    })
    return server
```

**Key Tests:**
- `test_mcp_client.py`: Tool invocation, retry logic, response validation
- `test_mcp_exceptions.py`: Exception hierarchy, error classification

---

### 3. API Tests (`tests/api/`)

**Purpose:** Test FastAPI endpoints without real agent execution

**Mock Strategy:**
- Use FastAPI TestClient
- Mock agent dependencies (PlannerAgent, WorkerAgent, JudgeAgent)
- Mock Redis state persistence

**Example:**
```python
from fastapi.testclient import TestClient
from chimera.main import app

client = TestClient(app)

def test_submit_goal():
    response = client.post("/planner/tasks", json={
        "goal": "Research trending AI topics"
    })
    assert response.status_code == 202
```

**Key Tests:**
- `test_api_planner.py`: Goal submission, task retrieval, validation
- `test_api_worker.py`: Task execution, status monitoring, timeout validation
- `test_api_judge.py`: Quality assessment, HITL routing, review approval/rejection

---

### 4. Orchestration Tests (`tests/orchestration/`)

**Purpose:** Test LangGraph state machine without real agent execution

**Mock Strategy:**
- Mock agent node functions
- Mock state transitions
- Simulate HITL interrupts

**Example:**
```python
def test_hitl_interrupt():
    context = {"judge_result": {"confidence": 0.75}}
    new_state = state_machine.transition("EVALUATE_RESULT", context)
    assert new_state == "HITL_REVIEW"
```

**Key Tests:**
- `test_langgraph_state.py`: State transitions, HITL interrupts, invalid transitions

---

### 5. Governor Tests (`tests/governor/`) - TDD Failing Tests

**Purpose:** Define "empty slots" for AI agent implementation using TDD

**TDD Strategy:**
- All tests MUST FAIL on first run (TDD goalposts)
- Tests define expected behavior before implementation
- Success is defined as the test failing with "not yet implemented - TDD goalpost"

**Mock Strategy:**
- Mock all dependencies (even though tests will fail)
- Define expected interfaces and contracts
- Document expected inputs/outputs in docstrings

**Example:**
```python
def test_fetch_trends_returns_correct_structure(self, trend_fetcher):
    """
    Test that fetch_trends() returns data matching API contract.

    Expected Outputs:
        - trends: List[dict] with topic, volume, sentiment, timestamp
        - metadata: dict with platform, location, timeframe

    Failure Modes:
        - MUST FAIL: TrendFetcher.fetch_trends() not yet implemented
    """
    pytest.fail("fetch_trends() method not yet implemented - TDD goalpost")
```

**Key Tests:**
- `test_trend_fetcher.py`: Trend data structure, MCP timeout handling, platform validation, Tenx Sense logging, rate limits
- `test_skills_interface.py`: Skill registry, parameter validation, execution output, MCP vs Skills distinction, schema introspection

**TDD Verification:**
```bash
# Run governor tests - all should FAIL
make test

# Expected output:
# FAILED test_trend_fetcher.py::TestTrendFetcher::test_fetch_trends_returns_correct_structure
# FAILED test_trend_fetcher.py::TestTrendFetcher::test_fetch_trends_handles_mcp_timeout
# ... (all tests fail with "not yet implemented - TDD goalpost")
```

---

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/agents/test_planner.py
```

### Run Specific Test Class
```bash
pytest tests/agents/test_planner.py::TestPlannerAgent
```

### Run Specific Test Method
```bash
pytest tests/agents/test_planner.py::TestPlannerAgent::test_plan_tasks_valid_goal
```

### Run with Coverage
```bash
pytest --cov=src/chimera --cov-report=html tests/
```

### Run with Verbose Output
```bash
pytest -v tests/
```

---

## Mock Guidelines

### DO Mock:
- ✅ LLM API calls (LiteLLM)
- ✅ MCP server connections
- ✅ Redis database operations
- ✅ External HTTP requests
- ✅ Time-dependent operations (datetime.utcnow)

### DO NOT Mock:
- ❌ Pydantic validation logic
- ❌ Pure Python functions (no side effects)
- ❌ Data structure transformations
- ❌ Business logic calculations

---

## Test Naming Convention

**Pattern:** `test_<function_name>_<scenario>`

**Examples:**
- `test_plan_tasks_valid_goal` - Happy path
- `test_plan_tasks_goal_too_vague` - Error case
- `test_execute_task_retry_on_transient_error` - Retry logic
- `test_assess_content_tier1_auto_approve` - HITL routing

---

## Assertion Guidelines

### Good Assertions:
```python
# Specific value checks
assert result["status"] == "success"
assert result["confidence"] > 0.90

# Type checks
assert isinstance(result["tasks"], list)

# Structure checks
assert "mcp_trace" in result
assert len(result["tasks"]) > 0
```

### Bad Assertions:
```python
# Too vague
assert result is not None

# Too brittle
assert result == {"status": "success", "timestamp": "2026-02-06T19:00:00Z"}
```

---

## Governor Mode Compliance

✅ **No Real Network Calls:** All external dependencies mocked  
✅ **No Real LLM Calls:** LiteLLM responses mocked  
✅ **No Real MCP Calls:** MCP server responses mocked  
✅ **No Real Database Calls:** Redis operations mocked  
✅ **Comprehensive Docstrings:** Purpose, inputs, outputs, failure modes documented  
✅ **Spec Alignment:** All tests reference spec sections  

---

## Future Enhancements

### Integration Tests (Day 3)
- Test full workflow: goal submission → planning → execution → evaluation
- Use real Redis (with cleanup)
- Use mock MCP server (not real Tenx Sense)
- Use mock LLM (LiteLLM mock mode)

### End-to-End Tests (Day 3)
- Test complete user journey
- Use Docker Compose for dependencies
- Use real FastAPI server
- Verify HITL workflow with simulated human reviewer

---

## References

- specs/technical.md Section 9 (Testing Contracts)
- .cursor/rules Section 9 (Testing Requirements)
- pyproject.toml (pytest configuration)

