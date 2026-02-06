"""
MCP Integration Module for Project Chimera.

This module provides MCP client functionality and exception classes
for interacting with MCP servers (Tenx Sense, platform APIs).

Spec Reference: specs/technical.md Section 5 (MCP Integration)
"""

from .mcp_client import MCPClient
from .mcp_exceptions import (
    MCPError,
    MCPServerUnavailableError,
    MCPToolNotFoundError,
    MCPAuthenticationError,
    MCPTimeoutError,
    MCPRateLimitError,
    MCPValidationError,
    MCPResponseError,
)

__all__ = [
    "MCPClient",
    "MCPError",
    "MCPServerUnavailableError",
    "MCPToolNotFoundError",
    "MCPAuthenticationError",
    "MCPTimeoutError",
    "MCPRateLimitError",
    "MCPValidationError",
    "MCPResponseError",
]

