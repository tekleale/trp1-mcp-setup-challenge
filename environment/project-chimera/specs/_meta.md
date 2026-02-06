# Project Chimera: Specification Metadata

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** 2026-02-06  
**Spec Framework:** GitHub Spec Kit

---

## 1. Project Metadata

### 1.1 Project Identity
- **Name:** Project Chimera
- **Mission:** Autonomous AI Influencer Network - Agentic Infrastructure
- **Repository:** `environment/project-chimera/`
- **Python Version:** 3.12+
- **Package Manager:** uv 0.10.0

### 1.2 Stakeholders
- **Lead Architect:** Tekleab Alemayehu
- **Challenge:** Forward Deployed Engineer (FDE) Trainee
- **Authority:** Project Chimera SRS Document (Autonomous Influencer Network)
- **Traceability:** Tenx MCP Sense (mcppulse.10academy.org)

### 1.3 Repository Structure
```
project-chimera/
├── specs/                  # Specifications (source of truth)
│   ├── _meta.md           # This file
│   ├── functional.md      # Behavioral contracts
│   └── technical.md       # Implementation contracts
├── src/                   # Implementation (follows specs)
│   └── chimera/
│       ├── agents/        # Planner, Worker, Judge
│       ├── state/         # Pydantic schemas
│       ├── orchestration/ # LangGraph state machine
│       └── mcp/           # MCP integration
├── tests/                 # Test suite
├── pyproject.toml         # Dependencies & tooling
└── .env.example           # Configuration template
```

### 1.4 Spec Versioning
- Specs evolve via Git commits
- Breaking changes require version bump
- All implementation must reference spec version
- Specs are immutable once implementation begins (create new version instead)

---

## 2. Decision Log (Architecture Decision Records)

### ADR-001: Planner-Worker-Judge Pattern
**Date:** 2026-02-06  
**Status:** Accepted  
**Context:** Need agent orchestration pattern for autonomous influencer tasks  
**Decision:** Adopt FastRender Swarm (Planner-Worker-Judge) from SRS Section 3.1  
**Rationale:**
- **Separation of concerns:** Planning ≠ Execution ≠ Quality Control
- **Scalability:** Stateless Workers enable horizontal scaling
- **Quality gates:** Judge prevents low-quality output from reaching production
- **HITL integration:** Natural approval point at Judge stage

**Alternatives Rejected:**
- Single-agent: No quality control, monolithic prompts
- ReAct loop: Too many LLM calls, expensive
- Plan-and-Execute: No quality gate before execution

**Consequences:**
- Requires 3 LLM calls per task (cost: ~$0.05-0.15/task)
- Adds latency (~10-30s per task)
- Simplifies debugging (clear failure points)

---

### ADR-002: Redis for Task Queues
**Date:** 2026-02-06  
**Status:** Accepted  
**Context:** Need persistent task queue for Planner → Worker → Judge flow  
**Decision:** Use Redis with `redis-py` library  
**Rationale:**
- **Simplicity:** In-memory, single dependency
- **Performance:** Sub-millisecond latency
- **Persistence:** AOF/RDB for durability
- **Atomic operations:** LPUSH/RPOP for queue semantics

**Alternatives Rejected:**
- RabbitMQ: Over-engineered for 3-day timeline
- Celery: Adds complexity, not needed for prototype
- Database queue: Slower, requires polling

**Consequences:**
- Redis becomes single point of failure (acceptable for prototype)
- No built-in retry logic (must implement manually)
- Memory-bound (queue size limited by RAM)

---

### ADR-003: LiteLLM for Multi-Provider Support
**Date:** 2026-02-06  
**Status:** Accepted  
**Context:** Need to use Claude (Planner/Judge) and Gemini (Worker) efficiently  
**Decision:** Use LiteLLM as unified interface  
**Rationale:**
- **Cost optimization:** Easy to switch models based on task complexity
- **Fallback:** Automatic retry with different provider
- **Observability:** Built-in token tracking
- **Consistency:** Same API for all providers

**Alternatives Rejected:**
- Direct SDKs: Requires separate code paths for each provider
- LangChain LLMs: Heavier abstraction, slower iteration

**Consequences:**
- Additional dependency
- Slight performance overhead (~50ms per call)
- Vendor lock-in to LiteLLM API patterns

---

### ADR-004: LangGraph for Orchestration
**Date:** 2026-02-06
**Status:** Accepted
**Context:** Need state machine for Planner → Worker → Judge with HITL interrupts
**Decision:** Use LangGraph StateGraph with conditional edges
**Rationale:**
- **HITL native:** Built-in interrupt/resume for human approval
- **Visualization:** Graph structure aids debugging
- **Type safety:** Works with Pydantic schemas
- **Persistence:** State checkpointing for long-running tasks

**Alternatives Rejected:**
- Custom orchestration: Reinventing the wheel
- Temporal/Airflow: Over-engineered for agent workflows

**Consequences:**
- Learning curve for LangGraph API
- Tight coupling to LangChain ecosystem
- Excellent fit for SRS requirements (Section 7.1)

---

### ADR-005: MCP vs A2A Protocol Boundaries
**Date:** 2026-02-06
**Status:** Accepted
**Context:** Confusion between MCP (Model Context Protocol) and A2A (Agent-to-Agent)
**Decision:**
- **MCP:** For tool/data access (Twitter API, Tenx Sense, web search)
- **A2A:** For future agent-to-agent communication (out of scope for Day 2-3)

**Rationale:**
- MCP is mature and required (FR 4.0 in SRS)
- A2A is experimental (defer to Month 2+ per Day 1 report)
- Clear separation prevents scope creep

**Consequences:**
- Day 2-3 focuses exclusively on MCP integration
- A2A remains in specs as future extension point
- No inter-agent communication in prototype

---

## 3. Spec Governance

### 3.1 How Specs Evolve
1. **Proposal:** Create GitHub issue or discussion
2. **Draft:** Update spec in feature branch
3. **Review:** Peer review (or self-review for solo work)
4. **Approval:** Merge to main
5. **Implementation:** Code follows approved spec

### 3.2 Approval Process
- **Solo work:** Self-approval after 24-hour cooling period
- **Team work:** Requires 1 approver
- **Breaking changes:** Requires all stakeholders

### 3.3 Relationship to SRS Document
- **SRS = Requirements:** What the business needs
- **Specs = Design:** How we'll build it
- **Code = Implementation:** The actual system

**Traceability:**
- Every spec section references SRS section
- Every test references spec section
- Every commit references spec version

### 3.4 Testing Requirements Per Spec
- **functional.md:** Acceptance tests (behavior verification)
- **technical.md:** Unit + integration tests (contract verification)
- **_meta.md:** No tests (metadata only)

**Coverage target:** 80% for Day 3 submission

---

## 4. Constraints & Non-Negotiables

### 4.1 Technical Constraints
- ✅ Python 3.12+ only (no backwards compatibility)
- ✅ MCP Sense traceability mandatory (FR 4.0)
- ✅ No secrets in version control (security requirement)
- ✅ Spec-first development (no code without spec)
- ✅ Type hints required (mypy strict mode)

### 4.2 Timeline Constraints
- ✅ Day 2 (Feb 6): Specs + core implementation
- ✅ Day 3 (Feb 7): Testing + containerization + documentation
- ✅ No scope creep beyond SRS Phase 1 (Section 7.1)

### 4.3 Quality Constraints
- ✅ All Pydantic schemas must validate
- ✅ All LangGraph edges must have conditions
- ✅ All MCP calls must have error handling
- ✅ All HITL flows must have timeout handling

### 4.4 Governance Constraints
- ✅ Specs are source of truth (code follows specs, not vice versa)
- ✅ No implementation code in spec files
- ✅ No assumptions beyond SRS and Challenge text
- ✅ Write like principal engineer, not marketing

---

**End of Metadata Specification**

