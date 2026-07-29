# Runs the constitution-lint MCP server over stdio.
# Build:  docker build -t constitution-lint-mcp .
# Run:    docker run -i --rm constitution-lint-mcp
FROM python:3.12-slim

WORKDIR /app
COPY constitution_lint.py constitution_lint_mcp.py ./

ENTRYPOINT ["python", "constitution_lint_mcp.py"]
