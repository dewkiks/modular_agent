#agent.py
from typing import List, Optional, Any, Dict
from agno.agent import Agent
from schemas import AgentNodeConfig, ModelConfig
from llm_adapter import LLMAdapter
from mcp_adapter import MCPAdapter


class AgentNode:
    """Simple Agent Node for workflow execution"""

    def __init__(self, config: AgentNodeConfig, mcp_config: Optional[Dict[str, Any]] = None):
        self.config = config
        self.mcp_config = mcp_config
        self.agent = None
        self.mcp_tools = None

    async def initialize(self):
        """Initialize agent with model and tools (async for MCP)"""
        model = LLMAdapter.create_model(self.config.model)
        tools = await self._load_tools()

        self.agent = Agent(
            model=model,
            tools=tools,
            instructions=self.config.system_prompt,
            markdown=self.config.markdown,
        )

    async def _load_tools(self) -> List:
        """Load both native and MCP tools"""
        tools = []

        # Load native tools
        tools.extend(self._load_native_tools())

        # Load MCP tools if config provided
        if self.mcp_config:
            self.mcp_tools = await MCPAdapter.load_mcp_tools(self.mcp_config)
            if self.mcp_tools:
                # Enter the async context manager
                await self.mcp_tools.__aenter__()
                tools.append(self.mcp_tools)

        return tools
    
    def _load_native_tools(self) -> List:
        """Load native Agno tools"""
        tool_instances = []

        for tool_name in self.config.tools:
            try:
                if tool_name == 'HackerNewsTools':
                    from agno.tools.hackernews import HackerNewsTools
                    tool_instances.append(HackerNewsTools())
                elif tool_name == 'DuckDuckGoTools':
                    from agno.tools.duckduckgo import DuckDuckGoTools
                    tool_instances.append(DuckDuckGoTools())
                else:
                    print(f"Warning: Unknown tool '{tool_name}'")

            except ImportError as e:
                print(f"Warning: Could not import tool '{tool_name}': {e}")
            except Exception as e:
                print(f"Warning: Error initializing tool '{tool_name}': {e}")

        return tool_instances
    
    async def execute(self, prompt: str, input_from_previous: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute the agent with a prompt (async)
        Args:
            prompt: The user prompt/query
            input_from_previous: Optional context from previous node
        """
        if not self.agent:
            await self.initialize()

        if input_from_previous:
            full_prompt = f"Context from previous step:\n{input_from_previous}\n\nQuery: {prompt}"
        else:
            full_prompt = prompt

        if self.mcp_tools:
            response = await self.agent.arun(full_prompt)
        else:
            response = self.agent.run(full_prompt)

        content = response.content if hasattr(response, 'content') else str(response)

        return {
            "content": content,
            "metadata": {
                "model": self.config.model.model_id,
                "provider": self.config.model.provider,
                "tools_used": self.config.tools
            }
        }

    async def cleanup(self):
        """Cleanup MCP connections"""
        if self.mcp_tools:
            await self.mcp_tools.__aexit__(None, None, None)


if __name__ == "__main__":
    import asyncio

    async def main():
        search_agent = AgentNode(AgentNodeConfig(
            model=ModelConfig(
                provider="gemini",
                model_id="gemini-2.0-flash-exp",
                api_key="API_KEY_HERE"
            ),
            tools=["DuckDuckGoTools"],
            markdown=True
        ))

        node1_output = await search_agent.execute("Find information about Python asyncio")

        summary_agent = AgentNode(AgentNodeConfig(
            model=ModelConfig(
                provider="gemini",
                model_id="gemini-2.0-flash-exp",
                api_key="API_KEY_HERE"
            ),
            tools=[],
            system_prompt="You are a summarization expert. Provide concise summaries."
        ))

        node2_output = await summary_agent.execute(
            "Summarize this in 3 bullet points",
            input_from_previous=node1_output["content"]
        )

        print("Final Output:", node2_output["content"])

        await search_agent.cleanup()
        await summary_agent.cleanup()

    asyncio.run(main())