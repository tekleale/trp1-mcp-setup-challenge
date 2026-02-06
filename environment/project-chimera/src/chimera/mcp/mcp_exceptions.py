"""
MCP Exception Classes for Project Chimera.

Defines custom exceptions for MCP client operations.

Spec Reference: specs/functional.md Section 4.3 (Tool Invocation Contracts)
"""


class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    pass


class MCPServerUnavailableError(MCPError):
    """
    Raised when MCP server cannot be reached.
    
    Causes:
        - Network connectivity issues
        - Server is down or not responding
        - Invalid server URL
        - Firewall blocking connection
    
    Recovery:
        - Retry with exponential backoff (transient error)
        - Check network connectivity
        - Verify server URL in configuration
        - Alert operations team if persistent
    
    Spec Reference: specs/functional.md Section 2.2 (Worker Agent - Retry/Timeout Policies)
    """
    pass


class MCPToolNotFoundError(MCPError):
    """
    Raised when requested MCP tool does not exist on server.
    
    Causes:
        - Tool name is misspelled
        - Tool not available on this MCP server
        - Server version mismatch (tool deprecated)
    
    Recovery:
        - Fail immediately (permanent error, no retry)
        - Log error to Tenx Sense
        - Return error to caller with suggested alternatives
    
    Spec Reference: specs/functional.md Section 2.2 (Worker Agent - Retry/Timeout Policies)
    """
    pass


class MCPAuthenticationError(MCPError):
    """
    Raised when MCP authentication fails.
    
    Causes:
        - Invalid API key
        - Expired credentials
        - Missing TENX_API_KEY environment variable
        - Insufficient permissions for requested tool
    
    Recovery:
        - Fail immediately (permanent error, no retry)
        - Alert operations team
        - Check environment configuration
        - Verify API key is valid and not expired
    
    Spec Reference: specs/functional.md Section 2.2 (Worker Agent - Retry/Timeout Policies)
    """
    pass


class MCPTimeoutError(MCPError):
    """
    Raised when MCP tool execution exceeds timeout.
    
    Causes:
        - Tool execution takes longer than task.timeout
        - Network latency
        - Server overload
        - Tool performing expensive computation
    
    Recovery:
        - Retry once with same timeout (transient error)
        - If retry fails, return timeout status to caller
        - Log timeout to Tenx Sense for monitoring
    
    Spec Reference: specs/functional.md Section 2.2 (Worker Agent - Retry/Timeout Policies)
    Spec Reference: specs/technical.md Section 2.2 (Task Schema - timeout field)
    """
    pass


class MCPRateLimitError(MCPError):
    """
    Raised when MCP server rate limit is exceeded.
    
    Causes:
        - Too many requests in short time period
        - Server-side rate limiting policy
        - Shared API key across multiple sessions
    
    Recovery:
        - Retry with exponential backoff (transient error)
        - Wait for rate limit window to reset
        - Log rate limit event to Tenx Sense
        - Consider implementing client-side rate limiting
    
    Spec Reference: specs/functional.md Section 2.2 (Worker Agent - Retry/Timeout Policies)
    """
    pass


class MCPValidationError(MCPError):
    """
    Raised when MCP request or response validation fails.
    
    Causes:
        - Invalid parameters for tool
        - Response does not match expected schema
        - Missing required fields in request
        - Type mismatch in parameters
    
    Recovery:
        - Fail immediately (permanent error, no retry)
        - Log validation error with details
        - Return error to caller with validation details
    
    Spec Reference: specs/technical.md Section 2.2 (Task Schema - parameters field)
    """
    pass


class MCPResponseError(MCPError):
    """
    Raised when MCP server returns an error response.
    
    Causes:
        - Server-side error during tool execution
        - Invalid tool parameters
        - Tool execution failed
        - Server internal error
    
    Recovery:
        - Check error type to determine if retryable
        - Log error response to Tenx Sense
        - Return error to caller with server error details
    
    Spec Reference: specs/functional.md Section 2.2 (Worker Agent - Retry/Timeout Policies)
    """
    pass

