"""
Planner API Endpoints for Project Chimera.

Provides REST API for submitting goals and retrieving task plans.

Spec Reference: specs/technical.md Section 7 (API Contracts)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

router = APIRouter(prefix="/planner", tags=["planner"])


# Request/Response Schemas

class SubmitGoalRequest(BaseModel):
    """Request schema for submitting a new goal."""
    
    goal: str = Field(..., min_length=10, max_length=500, description="High-level objective")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    constraints: list[str] = Field(default_factory=list, description="Business rules")
    
    class Config:
        json_schema_extra = {
            "example": {
                "goal": "Research trending AI topics on Twitter",
                "context": {"platform": "twitter", "timeframe": "24h"},
                "constraints": ["no political content", "english only"]
            }
        }


class SubmitGoalResponse(BaseModel):
    """Response schema for goal submission."""
    
    session_id: str = Field(..., description="Unique session identifier")
    status: str = Field(..., description="Current workflow status")
    created_at: datetime = Field(..., description="Session creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "status": "planning",
                "created_at": "2026-02-06T19:41:00Z"
            }
        }


class GetTasksResponse(BaseModel):
    """Response schema for retrieving task plan."""
    
    session_id: str = Field(..., description="Session identifier")
    tasks: list[dict[str, Any]] = Field(..., description="List of planned tasks")
    reasoning: str = Field(..., description="Planning rationale")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "tasks": [
                    {
                        "id": "task_xyz789",
                        "type": "mcp_call",
                        "description": "Fetch trending topics from Twitter API",
                        "mcp_tool": "twitter_trends",
                        "parameters": {"location": "US", "limit": 10}
                    }
                ],
                "reasoning": "Decomposed goal into 3 atomic tasks",
                "estimated_duration": 15
            }
        }


# API Endpoints

@router.post("/tasks", response_model=SubmitGoalResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_goal(request: SubmitGoalRequest):
    """
    Submit a new goal for planning.
    
    Purpose:
        - Accept high-level goal from user
        - Create new session
        - Trigger Planner agent to decompose goal into tasks
        - Return session ID for tracking
    
    Inputs:
        - goal: High-level objective (string, 10-500 characters)
        - context: Additional information (dictionary)
        - constraints: Business rules (list of strings)
    
    Outputs:
        - session_id: Unique session identifier (string)
        - status: Current workflow status ("planning")
        - created_at: Session creation timestamp (ISO 8601)
    
    Failure Modes:
        - 400 Bad Request: Invalid goal (too short, too long, empty)
        - 422 Unprocessable Entity: Validation error (Pydantic)
        - 500 Internal Server Error: Planner agent failure
    
    Spec References:
        - specs/technical.md Section 7.1 (POST /tasks)
        - specs/functional.md Section 2.1 (Planner Agent)
        - specs/technical.md Section 2.1 (GlobalState Schema)
    
    Example:
        POST /planner/tasks
        {
            "goal": "Research trending AI topics on Twitter",
            "context": {"platform": "twitter", "timeframe": "24h"},
            "constraints": ["no political content", "english only"]
        }
        
        Response (202 Accepted):
        {
            "session_id": "sess_abc123",
            "status": "planning",
            "created_at": "2026-02-06T19:41:00Z"
        }
    """
    # Stub: Future implementation will:
    # 1. Validate request (Pydantic handles this)
    # 2. Generate session_id (UUID)
    # 3. Create GlobalState object
    # 4. Trigger Planner agent (async)
    # 5. Store state in Redis
    # 6. Log to Tenx Sense (action_type="goal_submitted")
    # 7. Return 202 Accepted with session_id
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Planner agent not yet implemented"
    )


@router.get("/tasks/{session_id}", response_model=GetTasksResponse)
async def get_tasks(session_id: str):
    """
    Retrieve task plan for a session.
    
    Purpose:
        - Fetch task plan generated by Planner agent
        - Return list of tasks with dependencies
        - Provide planning rationale and duration estimate
    
    Inputs:
        - session_id: Unique session identifier (path parameter)
    
    Outputs:
        - session_id: Session identifier (string)
        - tasks: List of planned tasks (list of Task objects)
        - reasoning: Planning rationale (string)
        - estimated_duration: Time estimate in minutes (integer)
    
    Failure Modes:
        - 404 Not Found: Session does not exist
        - 409 Conflict: Planning not yet complete
        - 500 Internal Server Error: State retrieval failure
    
    Spec References:
        - specs/technical.md Section 7.2 (GET /tasks/{session_id})
        - specs/technical.md Section 2.2 (Task Schema)
        - specs/functional.md Section 2.1 (Planner Agent)
    
    Example:
        GET /planner/tasks/sess_abc123
        
        Response (200 OK):
        {
            "session_id": "sess_abc123",
            "tasks": [...],
            "reasoning": "Decomposed goal into 3 atomic tasks",
            "estimated_duration": 15
        }
    """
    # Stub: Future implementation will:
    # 1. Validate session_id format (UUID)
    # 2. Retrieve GlobalState from Redis
    # 3. Check if planning is complete (status != "planning")
    # 4. Extract task_queue from state
    # 5. Return task plan with metadata
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Task retrieval not yet implemented"
    )

