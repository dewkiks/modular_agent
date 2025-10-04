# Agent Node (Agno + MCP)

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

### Installation

```bash
pip install -r requirements.txt
```

---

## Quick Start

You can interact with the agent in two ways:

1. As an HTTP API via FastAPI (`debug_route.py`)  
2. As a Python module (`AgentNode` from `agent.py`)


endpoint `POST /agent/run` with a JSON body

```json
{
  "prompt": "Summarize latest Reddit discussions about Python",
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.0-flash-exp",
    "api_key": "YOUR_GEMINI_API_KEY"
  },
  "mcp_config": {
    "mcpServers": {
      "reddit": { "command": "uvx", "args": ["mcp-server-reddit"] },
      "git": { "command": "uvx", "args": ["mcp-server-git"] }
    }
  },
  "native_tools": [],
  "markdown": true
}
```

The adapter converts this to `StdioServerParameters` and builds a `MultiMCPTools` instance automatically.

---
