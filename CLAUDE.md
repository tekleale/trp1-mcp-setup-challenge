# TRP 1 - MCP Setup Challenge

Assessment project demonstrating MCP server configuration and AI agent rules optimization.

## Project Purpose

This is a 1-hour technical assessment to verify foundational qualities in:
- Configuring MCP (Model Context Protocol) tools
- Creating effective AI agent rules files
- Documenting technical work and insights
- Demonstrating technical comprehension and AI curiosity

## Tech Stack

- **Language**: Python 3.12.10
- **IDE**: VS Code with Augment Agent
- **Tools**: Git, MCP servers
- **Documentation**: Markdown
- **OS**: Windows 11 (PowerShell)

## Project Structure

```
.
├── README.md                    # Main project overview
├── CLAUDE.md                    # This rules file
├── docs/
│   ├── setup-process.md        # MCP setup documentation
│   ├── rules-research.md       # Rules file research findings
│   └── insights-and-learnings.md # Key insights and learnings
├── rules/
│   ├── CLAUDE.md               # Current rules file
│   └── iterations/             # Rules file evolution
├── artifacts/
│   └── screenshots/            # Visual documentation
└── .vscode/
    └── mcp.json                # MCP server configuration
```

## Code Style & Conventions

### Documentation
- Use clear, descriptive markdown formatting
- Keep files under 150 lines when possible
- Use proper heading hierarchy (H1 → H2 → H3)
- Include code examples in fenced blocks with language tags
- Add tables for structured comparisons

### File Organization
- Group related documentation in `docs/` directory
- Keep configuration files in appropriate locations (`.vscode/`, root)
- Use descriptive file names (kebab-case for markdown files)
- Maintain clear directory structure

### Git Practices
- Write clear, descriptive commit messages
- Commit logical units of work
- Document all significant changes
- Keep repository clean and organized

## Common Commands

### Git Operations
```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "descriptive message"

# View history
git log --oneline
```

### Python (when needed)
```bash
# Full path to Python
C:\Users\tekleab.alemayehu\AppData\Local\Programs\Python\Python312\python.exe

# Check version
python --version
```

### MCP Operations
- **List servers**: Use VS Code Command Palette → "MCP: List Servers"
- **Restart server**: Use VS Code Command Palette → "MCP: Restart Server"
- **View logs**: Check VS Code Output panel → MCP

## Project Goals & Success Criteria

### Task 1: MCP Server Setup
- ✅ Configure Tenx MCP Analysis server in `.vscode/mcp.json`
- ✅ Verify server connection is active
- ✅ Document setup process thoroughly
- ✅ Test that interactions are being logged

### Task 2: Rules File Optimization
- ✅ Research best practices (Boris Cherny, Anthropic, community)
- ✅ Create effective rules file based on research
- ✅ Test rules with various prompts
- ✅ Iterate and improve based on results
- ✅ Document evolution in `rules/iterations/`

### Task 3: Documentation
- ✅ Document setup process in `docs/setup-process.md`
- ✅ Document research findings in `docs/rules-research.md`
- ✅ Document insights in `docs/insights-and-learnings.md`
- ✅ Include what worked, what didn't, and why

## Testing Approach

### Rules File Testing
1. Test with simple prompts (e.g., "create a new markdown file")
2. Test with complex prompts (e.g., "refactor the documentation structure")
3. Verify agent follows conventions consistently
4. Check if agent references rules appropriately
5. Iterate based on results

### Documentation Testing
1. Ensure all markdown renders correctly
2. Verify all links work
3. Check code examples are accurate
4. Confirm structure is logical and clear

## Anti-Patterns (Don't Do This)

### Documentation
- ❌ Don't create files without explicit need
- ❌ Don't make documentation overly verbose
- ❌ Don't skip examples when explaining concepts
- ❌ Don't forget to update docs when things change

### Rules Files
- ❌ Don't make rules too long (keep focused)
- ❌ Don't be vague ("write good code" is useless)
- ❌ Don't forget to test rules with actual prompts
- ❌ Don't set and forget (iterate based on results)

### Git
- ❌ Don't commit without testing
- ❌ Don't use vague commit messages
- ❌ Don't commit sensitive information
- ❌ Don't leave repository in messy state

## Key Insights

### MCP (Model Context Protocol)
- Open standard for AI models to use external tools
- Three transport types: stdio (local), HTTP (remote), SSE (legacy)
- Configuration in `mcp.json` with `servers` and `inputs` sections
- Enables non-invasive logging and tool integration

### Rules Files
- Shorter and more specific is better than long and vague
- Examples are crucial for clarity
- Should evolve with the project
- Save significant time by reducing repeated instructions
- Work best when tested and iterated

### AI Agent Collaboration
- Clear documentation helps agent understand context
- Specific instructions lead to better results
- Iterative refinement improves outcomes
- Testing rules is essential for effectiveness

## Notes

- Python 3.12.10 installed but not in PATH (use full path when needed)
- PowerShell execution policy may block scripts (use appropriate bypass)
- Tenx MCP server details to be provided by 10 Academy
- All work must be documented for assessment review

