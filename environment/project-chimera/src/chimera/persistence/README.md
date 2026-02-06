# Persistence Module

## Overview

This module provides state persistence for Project Chimera using Redis. It handles storage and retrieval of GlobalState sessions, task queues, and review queues with TTL policies for automatic cleanup.

**Spec Reference:** specs/technical.md Section 2 (State Management)

---

## Module Purpose

### What is the Persistence Module?

The Persistence Module serves as the **data layer** for Project Chimera, enabling:
- **Session persistence:** Store GlobalState objects across API requests
- **Task queue management:** Persist tasks for Worker execution
- **Review queue management:** Store pending HITL reviews
- **TTL policies:** Automatic cleanup of expired sessions/tasks/reviews
- **Optimistic Concurrency Control (OCC):** Prevent race conditions with version numbers

### Why Redis?

**Spec Requirement:** specs/technical.md Section 8.1 mandates Redis for state management.

**Benefits:**
- **In-memory performance:** Fast read/write for agent orchestration
- **TTL support:** Automatic expiration for cleanup
- **Atomic operations:** INCR, LPUSH, RPOP for queue management
- **Pub/Sub:** Future support for real-time notifications
- **Persistence:** Optional disk persistence for durability

---

## Components

### PersistenceManager Class

**File:** `persistence.py`  
**Purpose:** Centralized interface for all Redis operations

**Initialization:**
```python
from chimera.persistence import PersistenceManager

persistence = PersistenceManager(redis_url="redis://localhost:6379/0")
```

---

## Methods

### 1. `save_session(session: dict) -> bool`

**Purpose:** Save GlobalState session to Redis

**Inputs:**
- `session`: GlobalState dict with session_id, goal, task_queue, status, version

**Outputs:**
- `success`: Boolean indicating save success

**Redis Operations:**
1. `SET session:{session_id} {json}` - Store session
2. `EXPIRE session:{session_id} 86400` - Set 24-hour TTL
3. Increment version for OCC

**Failure Modes:**
- `RedisConnectionError`: Redis unavailable
- `ValidationError`: Invalid session structure
- `VersionConflictError`: OCC version mismatch

**Example:**
```python
session = {
    "session_id": "sess_abc123",
    "goal": "Research trending AI topics",
    "status": "planning",
    "version": 1
}
success = await persistence.save_session(session)
```

---

### 2. `get_session(session_id: str) -> Optional[dict]`

**Purpose:** Retrieve GlobalState session from Redis

**Inputs:**
- `session_id`: Unique session identifier

**Outputs:**
- `session`: GlobalState dict or None if not found

**Redis Operations:**
1. `GET session:{session_id}` - Retrieve session
2. Deserialize JSON to dict
3. Validate with Pydantic

**Failure Modes:**
- `RedisConnectionError`: Redis unavailable
- `SessionNotFoundError`: Session does not exist or expired

**Example:**
```python
session = await persistence.get_session("sess_abc123")
if session:
    print(session["goal"])
```

---

### 3. `save_task(task: dict) -> bool`

**Purpose:** Save task to Redis task queue

**Inputs:**
- `task`: Task dict with id, type, mcp_tool, parameters, timeout

**Outputs:**
- `success`: Boolean indicating save success

**Redis Operations:**
1. `SET task:{task_id} {json}` - Store task
2. `LPUSH task_queue:{session_id} {task_id}` - Add to queue
3. `EXPIRE task:{task_id} 86400` - Set 24-hour TTL

**Failure Modes:**
- `RedisConnectionError`: Redis unavailable
- `ValidationError`: Invalid task structure

**Example:**
```python
task = {
    "id": "task_xyz789",
    "type": "mcp_call",
    "mcp_tool": "twitter_trends",
    "parameters": {"location": "US"}
}
success = await persistence.save_task(task)
```

---

### 4. `get_task(task_id: str) -> Optional[dict]`

**Purpose:** Retrieve task from Redis

**Inputs:**
- `task_id`: Unique task identifier

**Outputs:**
- `task`: Task dict or None if not found

**Redis Operations:**
1. `GET task:{task_id}` - Retrieve task
2. Deserialize JSON to dict
3. Validate with Pydantic

**Example:**
```python
task = await persistence.get_task("task_xyz789")
if task:
    print(task["mcp_tool"])
```

---

### 5. `save_review(review: dict) -> bool`

**Purpose:** Save review to Redis review queue

**Inputs:**
- `review`: ReviewItem dict with review_id, task_id, confidence, expires_at

**Outputs:**
- `success`: Boolean indicating save success

**Redis Operations:**
1. `SET review:{review_id} {json}` - Store review
2. `LPUSH review_queue {review_id}` - Add to queue
3. `EXPIRE review:{review_id} {ttl}` - Set TTL based on expires_at

**Failure Modes:**
- `RedisConnectionError`: Redis unavailable
- `ValidationError`: Invalid review structure

**Example:**
```python
review = {
    "review_id": "rev_abc123",
    "task_id": "task_xyz789",
    "confidence": 0.75,
    "expires_at": "2026-02-07T21:00:00Z"
}
success = await persistence.save_review(review)
```

---

### 6. `get_review(review_id: str) -> Optional[dict]`

**Purpose:** Retrieve review from Redis

**Inputs:**
- `review_id`: Unique review identifier

**Outputs:**
- `review`: ReviewItem dict or None if not found or expired

**Redis Operations:**
1. `GET review:{review_id}` - Retrieve review
2. Check if expired (compare expires_at with current time)
3. Return review or None

**Example:**
```python
review = await persistence.get_review("rev_abc123")
if review:
    print(review["confidence"])
```

---

## Redis Key Schema

```
session:{session_id}           # GlobalState JSON
task:{task_id}                 # Task JSON
review:{review_id}             # ReviewItem JSON
task_queue:{session_id}        # List of task IDs
review_queue                   # List of review IDs
```

**TTL Policies:**
- Sessions: 24 hours (86400 seconds)
- Tasks: 24 hours (86400 seconds)
- Reviews: Based on expires_at (default 24 hours)

---

## Optimistic Concurrency Control (OCC)

**Purpose:** Prevent race conditions when multiple processes update the same session

**Mechanism:**
1. Each session has a `version` field (integer)
2. On save, check if Redis version matches local version
3. If mismatch, raise `VersionConflictError`
4. On success, increment version

**Example:**
```python
# Process A reads session (version=1)
session_a = await persistence.get_session("sess_123")

# Process B reads session (version=1)
session_b = await persistence.get_session("sess_123")

# Process A updates session (version=1 → 2)
session_a["status"] = "executing"
await persistence.save_session(session_a)  # Success

# Process B tries to update session (version=1, but Redis has version=2)
session_b["status"] = "failed"
await persistence.save_session(session_b)  # Raises VersionConflictError
```

---

## Implementation Status

**Current:** Skeleton with method stubs and comprehensive docstrings  
**Next Steps:**
1. Implement Redis connection pool initialization
2. Implement save/get methods with real Redis operations
3. Add Pydantic validation for all data structures
4. Implement OCC version checking
5. Add error handling and retry logic
6. Write unit tests with fakeredis

---

## Governor Mode Compliance

✅ **No Real Database Connections:** All methods are stubs  
✅ **Comprehensive Docstrings:** Purpose, inputs, outputs, failure modes documented  
✅ **Redis Key Schema Defined:** Clear naming convention  
✅ **TTL Policies Specified:** 24-hour default for all entities  
✅ **OCC Mechanism Documented:** Version-based concurrency control  
✅ **Spec Alignment:** All contracts match specs/technical.md Section 2  

---

## Testing Requirements

**Unit Tests Required:**
- `tests/persistence/test_persistence.py`
  - Test save/get operations with fakeredis
  - Test TTL expiration
  - Test OCC version conflicts
  - Test error handling (Redis unavailable)

**Mock Strategy:**
```python
import fakeredis.aioredis as fakeredis

@pytest.fixture
async def persistence():
    redis = fakeredis.FakeRedis(decode_responses=True)
    return PersistenceManager(redis_client=redis)
```

**Spec Reference:** specs/technical.md Section 9 (Testing Contracts)

---

## References

- specs/technical.md Section 2 (State Management)
- specs/technical.md Section 8.1 (Environment Configuration - REDIS_URL)
- .cursor/rules Section 6 (State Management Rules)

