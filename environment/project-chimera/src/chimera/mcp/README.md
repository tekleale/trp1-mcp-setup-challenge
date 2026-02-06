# MCP Integration Module

## Overview

This module provides the MCP (Model Context Protocol) client for Project Chimera. It handles all interactions with MCP servers, including Tenx MCP Sense for traceability and future platform APIs (Twitter, content generation, web search).

**Spec Reference:** specs/technical.md Section 5 (MCP Integration)

---

## Module Purpose

### What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes how AI agents interact with external tools, data sources, and services. It's similar to how LSP (Language Server Protocol) standardized IDE integrations.

**Key Characteristics:**
- **Client-server architecture:** Agents (clients) connect to MCP servers (tools/data sources)
- **Transport:** Supports SSE (Server-Sent Events) and stdio-based connections
- **Primitives:** Tools, Resources, and Prompts as first-class concepts
- **Standardized:** Consistent interface across different tool providers

### Why MCP (Not Direct API Calls)?

**Spec Requirement:** specs/functional.md Section 4.1 mandates MCP for all external integrations.

**Benefits:**
- **Standardization:** Consistent interface for all external tools
- **Traceability:** All MCP calls logged to Tenx Sense (FR 4.0 requirement)
- **Swappability:** Easy to switch between tool providers
- **Error handling:** Centralized retry logic and error classification
- **Observability:** Structured logging and monitoring

**Forbidden:**
- ❌ Direct API calls: `requests.post("https://api.twitter.com/...")`
- ❌ Bypassing MCP: `httpx.get("https://example.com/...")`
- ❌ Skipping Tenx Sense logging

---

## Components

### 1. MCPClient

**File:** `mcp_client.py`  
**Class:** `MCPClient`

**Purpose:**  
Interface for calling MCP tools with automatic retry logic, timeout enforcement, and error handling.

**Key Methods:**

#### `call_tool(tool_name, parameters, timeout)`

**Purpose:** Invoke MCP tool with retry logic and error handling

**Inputs:**
- `tool_name`: Name of MCP tool (string)
- `parameters`: Tool parameters (dict)
- `timeout`: Maximum execution time in seconds (int, 5-300)

**Outputs:**
- `result`: Tool execution result (any type)
- `execution_time`: Time taken in seconds (float)
- `retry_count`: Number of retries performed (int)
- `mcp_trace`: MCP call metadata (dict)

**Retry Logic:**
- **Transient errors** (timeout, rate_limit, server_unavailable): Retry up to 3 times with exponential backoff (2s, 4s, 8s)
- **Permanent errors** (auth, tool_not_found, validation): Fail immediately, no retry

#### `validate_response(response)`

**Purpose:** Validate MCP response structure

**Inputs:**
- `response`: MCP response dictionary

**Outputs:**
- Boolean: True if valid, False otherwise

---

### 2. MCP Exceptions

**File:** `mcp_exceptions.py`

**Exception Hierarchy:**
```
MCPError (base)
├── MCPServerUnavailableError (retryable)
├── MCPToolNotFoundError (permanent)
├── MCPAuthenticationError (permanent)
├── MCPTimeoutError (retryable)
├── MCPRateLimitError (retryable)
├── MCPValidationError (permanent)
└── MCPResponseError (check error type)
```

**Error Classification:**

**Retryable Errors (Transient):**
- `MCPServerUnavailableError`: Network issues, server down
- `MCPTimeoutError`: Execution exceeded timeout
- `MCPRateLimitError`: Rate limit exceeded

**Permanent Errors (No Retry):**
- `MCPToolNotFoundError`: Tool doesn't exist
- `MCPAuthenticationError`: Invalid credentials
- `MCPValidationError`: Invalid parameters or response

**Conditional Errors:**
- `MCPResponseError`: Check error type to determine if retryable

---

## Usage by WorkerAgent

The WorkerAgent uses MCPClient to execute tasks that require external tools.

**Example Workflow:**

```python
from chimera.mcp import MCPClient, MCPTimeoutError, MCPAuthenticationError

class WorkerAgent:
    def __init__(self):
        self.mcp_client = MCPClient(server_name="tenxfeedbackanalytics")
    
    async def execute_task(self, task, mcp_server):
        try:
            # Call MCP tool
            result = await self.mcp_client.call_tool(
                tool_name=task["mcp_tool"],
                parameters=task["parameters"],
                timeout=task["timeout"]
            )
            
            return {
                "task_id": task["id"],
                "status": "success",
                "output": result["result"],
                "execution_time": result["execution_time"],
                "mcp_trace": result["mcp_trace"]
            }
        
        except MCPAuthenticationError as e:
            # Permanent error - fail immediately
            return {
                "task_id": task["id"],
                "status": "failure",
                "error": str(e),
                "error_type": "authentication_error"
            }
        
        except MCPTimeoutError as e:
            # Transient error - already retried by MCPClient
            return {
                "task_id": task["id"],
                "status": "timeout",
                "error": str(e),
                "error_type": "timeout_error"
            }
```

**Spec Reference:** specs/functional.md Section 2.2 (Worker Agent - MCP Tool Invocation Rules)

---

## MCP Servers (Phase 1)

### Tenx MCP Sense

**Server Name:** `tenxfeedbackanalytics`  
**Status:** ✅ Already Configured (`.vscode/mcp.json`)  
**Purpose:** Traceability and feedback analytics

**Configuration:**
- **URL:** `https://mcppulse.10academy.org/proxy`
- **Auth:** `TENX_API_KEY` environment variable
- **Transport:** stdio (uvx mcp-server-fetch)

**Tools:**
- `tenx_log_action`: Log agent action
- `tenx_query_sessions`: Query logged sessions

**Spec Reference:** specs/technical.md Section 5.1 (Tenx Sense Connection)

---

## Implementation Status

**Current:** Skeleton with method stubs and comprehensive docstrings  
**Next Steps:**
1. Implement MCP session initialization (stdio transport)
2. Implement `call_tool()` with real MCP protocol calls
3. Implement retry logic with exponential backoff
4. Implement response validation
5. Add Tenx Sense logging for all MCP calls
6. Write unit tests with mock MCP server

---

## Governor Mode Compliance

✅ **No Real Network Calls:** All methods are stubs  
✅ **Comprehensive Docstrings:** Purpose, inputs, outputs, failure modes documented  
✅ **Exception Classes Defined:** All MCP errors with recovery strategies  
✅ **Spec Alignment:** All contracts match specs/technical.md Section 5  
✅ **Usage Documentation:** Clear examples for WorkerAgent integration  

---

## Testing Requirements

**Unit Tests Required:**
- `tests/mcp/test_mcp_client.py`
  - Test `call_tool()` with mock MCP server
  - Test retry logic for transient errors
  - Test immediate failure for permanent errors
  - Test timeout enforcement
  - Test response validation

**Mock Strategy:**
```python
class MockMCPServer:
    async def call_tool(self, name, params):
        if name == "tenx_log_action":
            return {"logged": True, "trace_id": "mock_trace"}
        raise ValueError(f"Unknown tool: {name}")
```

**Spec Reference:** specs/technical.md Section 9.4 (MCP Server Test Doubles)

---

## References

- specs/technical.md Section 5 (MCP Integration)
- specs/functional.md Section 4 (MCP Integration Requirements)
- research/tooling_strategy.md (Tenx MCP Sense documentation)
- .cursor/rules Section 6.3 (MCP Integration Rules)

