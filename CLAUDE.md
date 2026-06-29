# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Python package of document-related tools (format conversion/processing) exposed over an **MCP server** (`FastMCP`) for use by AI assistants. Dependency and environment management is handled by `uv`.

## Commands

```bash
uv venv                     # create the virtual environment (.venv)
uv pip install -e .         # install the package in editable/development mode

uv run main.py              # start the MCP server (server name: "docs")
uv run pytest               # run all tests
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_pdf
                            # run a single test (file::Class::method)
```

## Architecture

The server is assembled in a single place and tools are deliberately decoupled from it:

- **`main.py`** — creates the `FastMCP("docs")` instance and registers tools. A tool only becomes available to the MCP client once it is registered here with `mcp.tool()(function)`. Defining a function in `tools/` is *not* enough — it must be wired up in `main.py`.
- **`tools/`** — each tool is a plain Python function (e.g. `tools/document.py`, `tools/math.py`). Functions take typed args and return a value; they have no knowledge of MCP. This keeps them directly unit-testable without a running server.
- **`tests/`** — pytest tests import tool functions directly and exercise them. Document tests read sample files from `tests/fixtures/` (`mcp_docs.docx`, `mcp_docs.pdf`) and assert on the converted output, so new document-conversion features generally need a matching fixture.

Document conversion in `tools/document.py` is layered: `binary_document_to_markdown` does the actual bytes→markdown conversion via `markitdown`, and `document_path_to_markdown` is a thin path-based wrapper that validates/reads a file (PDF or DOCX) and delegates to it. Prefer extending the binary function for new format logic so both entry points benefit.

## Defining MCP tools (conventions from README)

Tools are Python functions registered with the server:

```python
mcp.tool()(my_function)
```

Use pydantic `Field` for every parameter description, and write a comprehensive docstring:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does"),
) -> ReturnType:
    """Comprehensive docstring here"""
    # Implementation
```

Tool descriptions/docstrings should:
- Begin with a one-line summary.
- Provide a detailed explanation of functionality.
- Explain when to use (and when *not* to use) the tool.
- Include usage examples with expected input/output.

`tools/math.py::add` is the reference example of this docstring/`Field` style.

## Environment note (Windows + Python 3.14)

`pyproject.toml` pins `magika<0.6.3` via `[tool.uv] constraint-dependencies`. `magika` 0.6.3 caps `onnxruntime<=1.20.1` on win32, and that version has no wheel for CPython 3.14 — which breaks `uv run` (lockfile re-sync). Keep this constraint, or `uv lock --upgrade` will reintroduce the failure on Windows/Python 3.14.
