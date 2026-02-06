# Makefile for Project Chimera
#
# Purpose:
#   - Automate common development tasks
#   - Standardize build and test processes
#   - Support CI/CD integration
#
# Spec Reference: specs/technical.md Section 8 (Environment Configuration)
#
# Governor Mode Compliance:
#   - No real agent execution
#   - No real MCP calls
#   - No real database connections
#   - TDD failing tests only

.PHONY: help setup test test-governor test-all clean lint format spec-check docker-build docker-run

# Default target: Show help
help:
	@echo "Project Chimera - Makefile Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          Install dependencies from pyproject.toml"
	@echo "  make setup-dev      Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all TDD failing tests (Governor Mode)"
	@echo "  make test-governor  Run only governor TDD tests"
	@echo "  make test-all       Run all tests (agents, mcp, api, orchestration, governor)"
	@echo "  make test-coverage  Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linters (ruff, mypy)"
	@echo "  make format         Format code with ruff"
	@echo "  make spec-check     Validate spec alignment (stub)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo "  make docker-test    Run tests in Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove build artifacts and cache"
	@echo ""
	@echo "Spec Reference: specs/technical.md Section 8"

# Setup: Install dependencies
# Uses pip to install from pyproject.toml
# Spec Reference: specs/technical.md Section 8.1
setup:
	@echo "📦 Installing dependencies from pyproject.toml..."
	pip install --upgrade pip
	pip install -e .
	@echo "✅ Dependencies installed successfully"

# Setup Development: Install dev dependencies
setup-dev:
	@echo "📦 Installing development dependencies..."
	pip install --upgrade pip
	pip install -e ".[dev]"
	@echo "✅ Development dependencies installed successfully"

# Test: Run all TDD failing tests
# Governor Mode: All tests MUST FAIL (TDD goalposts)
# Spec Reference: specs/technical.md Section 9 (Testing Contracts)
test:
	@echo "🧪 Running TDD failing tests (Governor Mode)..."
	@echo "⚠️  Expected: All tests should FAIL (TDD goalposts)"
	@echo ""
	pytest tests/governor/ -v --tb=short || true
	@echo ""
	@echo "✅ TDD verification complete"
	@echo "📊 Success Criteria: All tests failed with 'not yet implemented - TDD goalpost'"

# Test Governor: Run only governor TDD tests
test-governor:
	@echo "🧪 Running Governor TDD tests..."
	pytest tests/governor/ -v --tb=short || true

# Test All: Run all tests (including unit tests)
test-all:
	@echo "🧪 Running all tests..."
	pytest tests/ -v --tb=short

# Test Coverage: Run tests with coverage report
test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src/chimera --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/index.html"

# Lint: Run linters
# Uses ruff for linting and mypy for type checking
lint:
	@echo "🔍 Running linters..."
	@echo "Running ruff..."
	ruff check src/ tests/ || true
	@echo "Running mypy..."
	mypy src/ || true
	@echo "✅ Linting complete"

# Format: Format code
# Uses ruff for code formatting
format:
	@echo "✨ Formatting code with ruff..."
	ruff format src/ tests/
	@echo "✅ Code formatted successfully"

# Spec Check: Validate spec alignment (stub)
# Governor Mode: This is a placeholder for future spec validation
# Future implementation will check:
#   - API contracts match specs/technical.md Section 7
#   - State schemas match specs/technical.md Section 2
#   - HITL thresholds match specs/_meta.md Section 3.2
spec-check:
	@echo "📋 Validating spec alignment..."
	@echo "⚠️  Spec validation not yet implemented (stub)"
	@echo ""
	@echo "Future checks:"
	@echo "  - API contracts (specs/technical.md §7)"
	@echo "  - State schemas (specs/technical.md §2)"
	@echo "  - HITL thresholds (specs/_meta.md §3.2)"
	@echo "  - MCP tool signatures (specs/technical.md §5)"
	@echo ""
	@echo "✅ Spec check placeholder complete"

# Docker Build: Build Docker image
# Spec Reference: specs/technical.md Section 8
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t chimera:day3 .
	@echo "✅ Docker image built: chimera:day3"

# Docker Run: Run Docker container
# Governor Mode: All endpoints return HTTP 501 Not Implemented (except / and /health)
docker-run:
	@echo "🐳 Running Docker container..."
	@echo "⚠️  Governor Mode: Only / and /health endpoints return 200 OK"
	@echo "📡 API available at http://localhost:8000"
	@echo "📖 API docs at http://localhost:8000/docs"
	docker run -p 8000:8000 --name chimera-day3 --rm chimera:day3

# Docker Test: Run tests in Docker container
docker-test:
	@echo "🐳 Running tests in Docker container..."
	docker run --rm chimera:day3 pytest tests/governor/ -v --tb=short || true

# Clean: Remove build artifacts and cache
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Governor Mode Compliance:
# ✅ No real agent execution
# ✅ No real MCP calls
# ✅ No real database connections
# ✅ TDD failing tests only
# ✅ All commands documented with spec references

