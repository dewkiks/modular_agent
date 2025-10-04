# Agent Node (Agno + MCP)\n\nA lightweight, extensible agent node built on top of the Agno framework. It supports multiple LLM providers (Gemini, Claude, OpenAI, Groq, Azure placeholder), native tools (DuckDuckGo, HackerNews), and MCP (Model Context Protocol) tools via `MultiMCPTools`.\n\nThis package exposes:\n\n- `agent.py` with `AgentNode` to execute prompts with a chosen provider and tools.\n- `llm_adapter.py` to create provider-specific model instances from a unified config.\n- `mcp_adapter.py` to load MCP servers and expose them as a single tool.\n- `schemas.py` with pydantic models for request/config validation.\n- `debug_route.py` exposing a minimal FastAPI route to run the agent over HTTP.\n\n## Project Structure\n\n```
agent/
├─ __init__.py
├─ agent.py
├─ llm_adapter.py
├─ mcp_adapter.py
├─ schemas.py
├─ debug_route.py
├─ agno_set.py                  # simple demo script
├─ requirements.txt
└─ README.md
```
\n## Requirements\n\n- Python 3.10+ recommended\n- See `requirements.txt` for pinned versions\n\nInstall dependencies:\n\n```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
\n## Quick Start\n\nYou can interact with the agent in two ways:\n\n1) As an HTTP API via FastAPI (`debug_route.py`)\n2) As a Python module (`AgentNode` from `agent.py`)\n\n### 1) Run the FastAPI server\n\n```bash
# From the agent/ directory
python -m uvicorn debug_route:app --host 0.0.0.0 --port 8000 --reload
```
\nThen call the endpoint `POST /agent/run` with the following JSON body (example uses Gemini + DuckDuckGo):\n\n```json
{
  "prompt": "Find information about Python asyncio",
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.0-flash-exp",
    "api_key": "YOUR_GEMINI_API_KEY"
  },
  "native_tools": ["DuckDuckGoTools"],
  "system_prompt": "You are a helpful assistant.",
  "markdown": true
}
```
\n- Response contains `content` (string) and `metadata` with basic model/tool info.\n- You may also pass `previous_node_output` to chain node results into a subsequent prompt.\n\n#### With MCP tools (optional)\n\nIf you want to enable MCP tools, add an `mcp_config` field. Example Claude-style configuration shape (the actual commands depend on the MCP servers you have installed):\n\n```json
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
      "git":    { "command": "uvx", "args": ["mcp-server-git"] }
    }
  },
  "native_tools": [],
  "markdown": true
}
```
\nThe adapter will convert these to `StdioServerParameters` and create a `MultiMCPTools` instance that is added to the agent's tools.\n\n### 2) Use `AgentNode` directly in Python\n\n```python
from agent import AgentNode
from schemas import AgentNodeConfig, ModelConfig
import asyncio

async def main():
    node = AgentNode(AgentNodeConfig(
        model=ModelConfig(
            provider="gemini",
            model_id="gemini-2.0-flash-exp",
            api_key="YOUR_GEMINI_API_KEY"
        ),
        tools=["DuckDuckGoTools"],
        markdown=True
    ))

    result = await node.execute("Find information about Python asyncio")
    print(result["content"])  # agent output
    await node.cleanup()

asyncio.run(main())
```
\nYou can also chain nodes by passing `input_from_previous` to `execute()` on subsequent nodes.\n\n## Supported Providers\n\nDefined in `schemas.ModelConfig.provider` and implemented in `llm_adapter.LLMAdapter.create_model()`:\n\n- `gemini` (via `agno.models.google.Gemini`)\n- `claude` (via `agno.models.anthropic.Claude`)\n- `openai` (via `agno.models.openai.OpenAIChat`)\n- `groq` (via `agno.models.groq.Groq`)\n- `azure` (placeholder in code; ensure you have `AzureOpenAIChat` imported and available before using)\n\n## Native Tools\n\nConfigured via the `tools` array in `AgentNodeConfig` and loaded by `AgentNode._load_native_tools()`:\n\n- `DuckDuckGoTools` (web search)\n- `HackerNewsTools` (HN top stories, etc.)\n\nUnknown tool names are ignored with a warning.\n\n## MCP Tools\n\n- MCP servers are optional and driven by the `mcp_config` you pass to the API or `AgentNode`.\n- `mcp_adapter.MCPAdapter` converts your config into `StdioServerParameters` and returns a `MultiMCPTools` instance.\n- The agent automatically enters/exits the MCP async context within `initialize()`/`cleanup()`.\n\n## Environment Variables & Secrets\n\n- Do not hardcode API keys. Prefer environment variables or a secure secret store.\n- This project currently accepts the `api_key` inside the `model` object of the request/config. In your own application, you can load from env and populate that field.\n- Example env variables you might keep in your host app or deployment platform:
  - `GEMINI_API_KEY`
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GROQ_API_KEY`
\n> Important: Never commit real API keys to your repository. Rotate any keys that may have been exposed.\n\n## Running the demo script\n\n`agno_set.py` includes a minimal demonstration that queries HackerNews using Gemini. Update the API key before running:
\n```bash
python agno_set.py
```
\n## requirements.txt (for GitHub installs)\n\nAll runtime dependencies are pinned in `requirements.txt`. GitHub users can install with:
\n```bash
pip install -r requirements.txt
```
\nIf you intend to use MCP servers, ensure you have any specific MCP server CLIs installed and available on PATH (e.g., via `uvx`).\n\n## Development Tips\n\n- Type checking/IDE assistance is easier with Python 3.10+.
- `pydantic` is used for request/config validation (`schemas.py`).
- `fastapi` + `uvicorn` power the HTTP route in `debug_route.py`.
- Logging and more robust error handling can be added as desired.
\n## Example cURL\n\n```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize the top 5 stories on Hacker News",
    "model": {
      "provider": "gemini",
      "model_id": "gemini-2.0-flash-exp",
      "api_key": "YOUR_GEMINI_API_KEY"
    },
    "native_tools": ["HackerNewsTools"],
    "markdown": true
  }'
```