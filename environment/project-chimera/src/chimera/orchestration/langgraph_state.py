"""
LangGraph State Machine Skeleton for Project Chimera.

This module defines the state machine structure for orchestrating
Planner-Worker-Judge agent workflows.

Spec Reference: specs/technical.md Section 3 (LangGraph State Machine)
"""

from typing import Literal, Any
from enum import Enum


class StateType(str, Enum):
    """Enumeration of all possible states in the workflow."""
    INIT = "init"
    EXECUTE_TASK = "execute_task"
    EVALUATE_RESULT = "evaluate_result"


class LangGraphStateMachine:
    """
    State machine for orchestrating agent workflows.
    
    This class defines the structure and transitions for the Planner-Worker-Judge
    pattern. Each state represents a phase in the agent workflow.
    
    Spec Reference: specs/technical.md Section 3.1 (Node Definitions)
    """
    
    def __init__(self):
        """Initialize the state machine with default configuration."""
        self.current_state: StateType = StateType.INIT
        self.state_history: list[StateType] = []
        self.transition_rules = self._define_transitions()
    
    def _define_transitions(self) -> dict[StateType, list[StateType]]:
        """
        Define allowed state transitions.
        
        Returns:
            Dictionary mapping each state to its allowed next states.
        
        Spec Reference: specs/technical.md Section 3.2 (Edge Conditions)
        """
        return {
            StateType.INIT: [StateType.EXECUTE_TASK],
            StateType.EXECUTE_TASK: [StateType.EVALUATE_RESULT, StateType.EXECUTE_TASK],
            StateType.EVALUATE_RESULT: [StateType.EXECUTE_TASK, StateType.INIT],
        }
    
    # State: Init
    def state_init(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Initial state: Set up workflow and prepare for task execution.
        
        Purpose:
            - Initialize session
            - Validate input goal
            - Prepare global state
        
        Inputs:
            - context["goal"]: High-level objective (string)
            - context["constraints"]: Business rules (list)
            - context["session_id"]: Unique session identifier (string)
        
        Outputs:
            - context["status"]: Set to "initialized"
            - context["task_queue"]: Empty list (to be populated by Planner)
            - context["session_metadata"]: Session initialization metadata
        
        Event Triggers:
            - On success: Transition to EXECUTE_TASK
            - On validation failure: Raise exception
        
        Spec Reference: specs/functional.md Section 2.1 (Planner Agent)
        """
        # Stub: Future implementation will call Planner agent
        return context
    
    # State: ExecuteTask
    def state_execute_task(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute task state: Worker agent executes next task from queue.
        
        Purpose:
            - Pop next task from task_queue
            - Execute task using appropriate skill or MCP tool
            - Store result in completed_tasks
        
        Inputs:
            - context["task_queue"]: List of pending tasks
            - context["session_id"]: Session identifier
            - context["mcp_client"]: MCP client for tool calls
        
        Outputs:
            - context["task_queue"]: Updated queue (task removed)
            - context["completed_tasks"]: Appended with WorkerResult
            - context["current_result"]: Most recent task result
        
        Event Triggers:
            - On success: Transition to EVALUATE_RESULT
            - On task queue empty: Transition to INIT (workflow complete)
            - On retry needed: Transition to EXECUTE_TASK (same state)
        
        Spec Reference: specs/functional.md Section 2.2 (Worker Agent)
        """
        # Stub: Future implementation will call Worker agent
        return context
    
    # State: EvaluateResult
    def state_evaluate_result(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate result state: Judge agent assesses quality and confidence.
        
        Purpose:
            - Evaluate most recent WorkerResult
            - Calculate confidence score
            - Determine if HITL review is required
        
        Inputs:
            - context["current_result"]: Most recent WorkerResult
            - context["original_task"]: Task that produced this result
            - context["brand_guidelines"]: Quality criteria
        
        Outputs:
            - context["confidence"]: Quality confidence score (0.0-1.0)
            - context["requires_review"]: Boolean flag for HITL
            - context["quality_metrics"]: Detailed quality assessment
        
        Event Triggers:
            - If confidence > 0.90: Auto-approve, transition to EXECUTE_TASK
            - If 0.70 <= confidence <= 0.90: HITL interrupt (human review)
            - If confidence < 0.70: Auto-reject, transition to EXECUTE_TASK
            - If task_queue empty: Transition to INIT (workflow complete)
        
        Spec Reference: specs/functional.md Section 2.3 (Judge Agent)
        Spec Reference: specs/functional.md Section 3.1 (HITL Three-Tier System)
        """
        # Stub: Future implementation will call Judge agent
        return context
    
    def transition(self, next_state: StateType, context: dict[str, Any]) -> dict[str, Any]:
        """
        Transition to next state if allowed.
        
        Args:
            next_state: Target state to transition to
            context: Current workflow context
        
        Returns:
            Updated context after state transition
        
        Raises:
            ValueError: If transition is not allowed
        
        Spec Reference: specs/technical.md Section 3.2 (Edge Conditions)
        """
        if next_state not in self.transition_rules[self.current_state]:
            raise ValueError(
                f"Invalid transition: {self.current_state} -> {next_state}. "
                f"Allowed: {self.transition_rules[self.current_state]}"
            )
        
        self.state_history.append(self.current_state)
        self.current_state = next_state
        return context

