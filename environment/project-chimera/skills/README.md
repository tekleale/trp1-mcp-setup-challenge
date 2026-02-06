# Runtime Agent Skills

## Skill 1: Task Decomposition

- **Purpose:** Break down high-level goals into atomic, executable tasks
- **Inputs:**
  - goal: High-level objective (string, 10-500 characters)
  - context: Additional information (dictionary)
  - constraints: Business rules (list of strings)
  - max_tasks: Maximum number of tasks (integer, 1-20)
- **Outputs:**
  - tasks: Ordered list of atomic tasks
  - reasoning: Planning rationale (string)
  - estimated_duration: Time estimate in minutes (integer)
  - dependency_graph: Task dependencies (dictionary)
  - confidence: Planner confidence score (float, 0.0-1.0)
- **Failure Modes:**
  - GoalTooVagueError: Goal is ambiguous or unclear
  - NoViablePlanError: Cannot create plan within constraints
  - CircularDependencyError: Detected circular task dependencies
  - InsufficientCapabilitiesError: Required skills or tools not available
- **Used By:** Planner Agent

## Skill 2: Content Quality Assessment

- **Purpose:** Evaluate quality of generated content and calculate confidence scores
- **Inputs:**
  - content: Generated content to evaluate (string)
  - content_type: Type of content (tweet, instagram_caption, tiktok_script)
  - original_task: Reference to the task that generated this content
  - brand_guidelines: Brand voice and style rules (dictionary)
- **Outputs:**
  - overall_score: Quality score (float, 0.0-1.0)
  - format_correctness: Format validation score (float, 0.0-1.0)
  - completeness: Completeness score (float, 0.0-1.0)
  - relevance: Relevance to task score (float, 0.0-1.0)
  - issues: List of quality issues with severity levels
  - recommendations: Suggested improvements (list of strings)
- **Failure Modes:**
  - UnsupportedContentTypeError: Content type not recognized
  - MissingGuidelinesError: Brand guidelines not provided
  - InvalidContentError: Content is empty or malformed
- **Used By:** Judge Agent

## Skill 3: MCP Tool Execution

- **Purpose:** Execute MCP tool calls with retry logic and error handling
- **Inputs:**
  - mcp_server: Server name (string, e.g., "tenxfeedbackanalytics")
  - tool_name: Tool to call (string, e.g., "tenx_log_action")
  - parameters: Tool parameters (dictionary)
  - timeout: Execution timeout in seconds (integer, 5-300)
  - retry_policy: Retry configuration (max_retries, backoff_seconds, retry_on_errors)
- **Outputs:**
  - result: Tool execution result (any type)
  - execution_time: Time taken in seconds (float)
  - retry_count: Number of retries performed (integer)
  - mcp_trace: MCP call metadata (dictionary)
- **Failure Modes:**
  - MCPServerUnavailableError: Cannot connect to MCP server
  - MCPToolNotFoundError: Tool does not exist on server
  - MCPAuthenticationError: Invalid credentials
  - MCPTimeoutError: Tool execution exceeded timeout
  - MCPRateLimitError: Rate limit exceeded
- **Used By:** Worker Agent


