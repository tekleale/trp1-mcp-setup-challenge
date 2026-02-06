"""
Worker API Endpoints for Project Chimera.

Provides REST API for task execution and status monitoring.

Spec Reference: specs/technical.md Section 7 (API Contracts)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime

router = APIRouter(prefix="/worker", tags=["worker"])


# Request/Response Schemas

class ExecuteTaskRequest(BaseModel):
    """Request schema for executing a task."""
    
    task_id: str = Field(..., description="Unique task identifier")
    task_type: Literal["mcp_call", "computation", "validation"] = Field(...)
    description: str = Field(..., min_length=5, max_length=200)
    mcp_tool: str | None = Field(None, description="MCP tool name")
    parameters: dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=60, ge=5, le=300, description="Timeout in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_xyz789",
                "task_type": "mcp_call",
                "description": "Fetch trending topics from Twitter API",
                "mcp_tool": "twitter_trends",
                "parameters": {"location": "US", "limit": 10},
                "timeout": 30
            }
        }


class ExecuteTaskResponse(BaseModel):
    """Response schema for task execution."""
    
    task_id: str = Field(..., description="Task identifier")
    status: Literal["success", "failure", "timeout"] = Field(...)
    output: Any | None = Field(None, description="Task execution result")
    error: str | None = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    mcp_trace: dict[str, Any] | None = Field(None, description="MCP call metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_xyz789",
                "status": "success",
                "output": {"trends": ["AI agents", "LangGraph", "MCP"]},
                "error": None,
                "execution_time": 2.34,
                "mcp_trace": {"server": "tenx_sense", "call_id": "call_123"}
            }
        }


class GetTaskStatusResponse(BaseModel):
    """Response schema for task status retrieval."""
    
    task_id: str = Field(..., description="Task identifier")
    status: Literal["pending", "running", "success", "failure", "timeout"] = Field(...)
    progress: float = Field(..., ge=0.0, le=1.0, description="Completion percentage")
    started_at: datetime | None = Field(None, description="Execution start time")
    completed_at: datetime | None = Field(None, description="Execution completion time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_xyz789",
                "status": "running",
                "progress": 0.65,
                "started_at": "2026-02-06T19:42:00Z",
                "completed_at": None
            }
        }


# API Endpoints

@router.post("/execute", response_model=ExecuteTaskResponse, status_code=status.HTTP_200_OK)
async def execute_task(request: ExecuteTaskRequest):
    """
    Execute a task using Worker agent.
    
    Purpose:
        - Execute individual task from Planner's task queue
        - Invoke MCP tools or perform computations
        - Return execution result with MCP trace
        - Handle timeouts and retries
    
    Inputs:
        - task_id: Unique task identifier (string)
        - task_type: Type of task (mcp_call, computation, validation)
        - description: Task description (string, 5-200 characters)
        - mcp_tool: MCP tool name (string, optional)
        - parameters: Tool parameters (dictionary)
        - timeout: Maximum execution time in seconds (int, 5-300)
    
    Outputs:
        - task_id: Task identifier (string)
        - status: Execution status (success, failure, timeout)
        - output: Task result (any type, null if failed)
        - error: Error message (string, null if success)
        - execution_time: Time taken in seconds (float)
        - mcp_trace: MCP call metadata (dict, null if no MCP call)
    
    Failure Modes:
        - 400 Bad Request: Invalid task parameters
        - 408 Request Timeout: Task execution exceeded timeout
        - 422 Unprocessable Entity: Validation error (Pydantic)
        - 500 Internal Server Error: Worker agent failure
        - 503 Service Unavailable: MCP server unavailable
    
    Spec References:
        - specs/functional.md Section 2.2 (Worker Agent)
        - specs/technical.md Section 2.3 (WorkerResult Schema)
        - specs/technical.md Section 5 (MCP Integration)
    
    Example:
        POST /worker/execute
        {
            "task_id": "task_xyz789",
            "task_type": "mcp_call",
            "description": "Fetch trending topics",
            "mcp_tool": "twitter_trends",
            "parameters": {"location": "US"},
            "timeout": 30
        }
        
        Response (200 OK):
        {
            "task_id": "task_xyz789",
            "status": "success",
            "output": {"trends": ["AI agents"]},
            "error": null,
            "execution_time": 2.34,
            "mcp_trace": {"server": "tenx_sense", "call_id": "call_123"}
        }
    """
    # Stub: Future implementation will:
    # 1. Validate request (Pydantic handles this)
    # 2. Retrieve task from Redis task queue
    # 3. Invoke Worker agent with task
    # 4. Worker calls MCP client if task_type == "mcp_call"
    # 5. Handle timeouts (asyncio.wait_for)
    # 6. Retry on transient errors (max 3 retries)
    # 7. Log to Tenx Sense (action_type="task_executed")
    # 8. Update GlobalState.completed_tasks
    # 9. Return WorkerResult
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Worker agent not yet implemented"
    )


@router.get("/status/{task_id}", response_model=GetTaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get execution status of a task.
    
    Purpose:
        - Monitor task execution progress
        - Check if task is pending, running, or complete
        - Provide execution timestamps
    
    Inputs:
        - task_id: Unique task identifier (path parameter)
    
    Outputs:
        - task_id: Task identifier (string)
        - status: Current status (pending, running, success, failure, timeout)
        - progress: Completion percentage (float, 0.0-1.0)
        - started_at: Execution start timestamp (ISO 8601, null if not started)
        - completed_at: Completion timestamp (ISO 8601, null if not complete)
    
    Failure Modes:
        - 404 Not Found: Task does not exist
        - 500 Internal Server Error: State retrieval failure
    
    Spec References:
        - specs/technical.md Section 2.2 (Task Schema)
        - specs/functional.md Section 2.2 (Worker Agent)
    
    Example:
        GET /worker/status/task_xyz789
        
        Response (200 OK):
        {
            "task_id": "task_xyz789",
            "status": "running",
            "progress": 0.65,
            "started_at": "2026-02-06T19:42:00Z",
            "completed_at": null
        }
    """
    # Stub: Future implementation will:
    # 1. Validate task_id format (UUID)
    # 2. Retrieve task from Redis
    # 3. Check task status in GlobalState
    # 4. Calculate progress based on execution time
    # 5. Return status with timestamps
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Task status retrieval not yet implemented"
    )

