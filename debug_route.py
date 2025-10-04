from fastapi import FastAPI
from schemas import AgentNodeConfig, AgentRunRequest
from agent import AgentNode

app = FastAPI()

@app.post("/agent/run")
async def run_agent(request: AgentRunRequest):
    """Run agent with unified configuration"""
    config = AgentNodeConfig(
        model=request.model,
        tools=request.native_tools or [],
        system_prompt=request.system_prompt,
        markdown=request.markdown
    )

    agent_node = AgentNode(config, request.mcp_config)

    try:
        result = await agent_node.execute(
            request.prompt,
            request.previous_node_output
        )
        return result
    finally:
        await agent_node.cleanup()
