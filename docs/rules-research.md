# Task 2: Rules File Research & Configuration

**Date:** February 2, 2026  
**Objective:** Research best practices for AI agent rules files and create effective configurations

## Overview

Rules files are configuration files that guide AI coding agents on how to work with your codebase, coding style, and preferences. They persist across sessions and save significant time by documenting project conventions.

## Rules File Locations by IDE

| IDE | Rules File Location |
|-----|---------------------|
| **VS Code (Copilot)** | `.github/copilot-instructions.md` |
| **Cursor** | `.cursor/rules/agent.mdc` |
| **Claude Code** | `CLAUDE.md` |
| **Augment (VS Code)** | Similar to Copilot, uses workspace context |

## Research Sources

### 1. Anthropic's Official Best Practices

**Source:** [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

Key principles from the Claude Code team:
- **Keep it concise**: Shorter, focused rules are more effective than lengthy documents
- **Be specific**: Vague instructions lead to inconsistent results
- **Use examples**: Show, don't just tell
- **Iterate based on results**: Test and refine your rules

### 2. Boris Cherny's Workflow (Creator of Claude Code)

**Key Insights from Community Research:**

Boris Cherny shared his 13-step workflow which emphasizes:

1. **Start with a one-liner** explaining what the project does
2. **Document your stack** (frameworks, languages, tools)
3. **Define coding conventions** (naming, structure, patterns)
4. **Specify testing approach** (framework, coverage expectations)
5. **List common commands** (build, test, deploy)
6. **Include anti-patterns** (what NOT to do)
7. **Use slash commands** for repeated "inner loop" workflows

**Boris's Key Quote:**
> "I use slash commands for every 'inner loop' workflow that I end up doing many times a day. This saves me from repeated prompting, and makes my workflow much faster."

### 3. Builder.io's CLAUDE.md Guide

**Best Practices Identified:**

#### Structure
1. **Open with context**: One-liner about the project
2. **Tech stack**: List all major technologies
3. **Code style**: Formatting, naming conventions
4. **Architecture**: How the code is organized
5. **Common tasks**: Frequent operations
6. **Gotchas**: Known issues or quirks

#### Common Mistakes to Avoid
- ❌ Making rules too long (8x longer than necessary)
- ❌ Being too vague or general
- ❌ Not updating rules as project evolves
- ❌ Forgetting to include examples
- ❌ Not testing rules with actual prompts

### 4. VS Code MCP Documentation

**Integration Points:**
- Rules files work alongside MCP servers
- Can reference MCP tools in rules
- Context engineering is key
- Rules should guide tool selection

## Best Practices Summary

### DO ✅

1. **Be Concise and Specific**
   - Short, actionable instructions
   - Specific examples over general guidelines
   - Focus on what matters most

2. **Document Your Stack**
   ```markdown
   ## Tech Stack
   - Language: Python 3.12
   - Framework: FastAPI
   - Database: PostgreSQL
   - Testing: pytest
   ```

3. **Define Code Style**
   ```markdown
   ## Code Style
   - Use type hints for all function signatures
   - Follow PEP 8
   - Max line length: 100 characters
   - Use descriptive variable names
   ```

4. **Include Common Commands**
   ```markdown
   ## Commands
   - Run tests: `pytest tests/`
   - Start server: `uvicorn main:app --reload`
   - Format code: `black .`
   ```

5. **Specify Testing Requirements**
   ```markdown
   ## Testing
   - Write tests for all new features
   - Maintain >80% coverage
   - Use fixtures for common setups
   ```

6. **List Anti-Patterns**
   ```markdown
   ## Don't Do This
   - Don't use global variables
   - Don't commit commented-out code
   - Don't skip error handling
   ```

### DON'T ❌

1. **Don't Make It Too Long**
   - Keep under 200 lines
   - Focus on essentials
   - Link to external docs for details

2. **Don't Be Vague**
   - ❌ "Write good code"
   - ✅ "Use type hints and docstrings for all public functions"

3. **Don't Forget Context**
   - Include project purpose
   - Explain architectural decisions
   - Document why, not just what

4. **Don't Set and Forget**
   - Update as project evolves
   - Remove outdated rules
   - Test rules regularly

## Key Insights from Research

### How Rules Change AI Agent Behavior

1. **Consistency**: Rules ensure the agent follows your conventions across all interactions
2. **Efficiency**: Reduces need to repeat instructions in every prompt
3. **Quality**: Guides agent toward better code that matches your standards
4. **Context**: Helps agent understand project structure and patterns

### Effective Rule Patterns

**Pattern 1: Stack Declaration**
```markdown
# Project: [Name]
[One-line description]

## Stack
- Frontend: React + TypeScript
- Backend: Node.js + Express
- Database: MongoDB
```

**Pattern 2: Style Guide**
```markdown
## Code Style
- Use functional components with hooks
- Prefer const over let
- Use async/await over promises
- Extract magic numbers to constants
```

**Pattern 3: Workflow Commands**
```markdown
## Common Tasks
/test - Run full test suite
/lint - Check code style
/build - Create production build
```

## Next Steps

1. Create initial rules file for this project
2. Test with various prompts
3. Iterate based on results
4. Document what works and what doesn't

