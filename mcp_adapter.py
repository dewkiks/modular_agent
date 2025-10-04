"""MCP Tools Adapter - Standalone MCP server management"""
from typing import List, Dict, Any, Optional
from mcp import StdioServerParameters
from agno.tools.mcp import MultiMCPTools


class MCPAdapter:
    """Manages MCP server connections and tool loading"""

    @staticmethod
    def create_server_params(mcp_config: Dict[str, Any]) -> List[StdioServerParameters]:
        """
        Convert MCP config to StdioServerParameters

        Args:
            mcp_config: Dict with server configs like Claude's format
                Example: {
                    "mcpServers": {
                        "reddit": {"command": "uvx", "args": ["mcp-server-reddit"]},
                        "git": {"command": "uvx", "args": ["mcp-server-git"]}
                    }
                }
        """
        server_params = []
        servers = mcp_config.get("mcpServers", {})

        for name, config in servers.items():
            params = StdioServerParameters(
                command=config.get("command", "uvx"),
                args=config.get("args", []),
                env=config.get("env")
            )
            server_params.append(params)

        return server_params

    @staticmethod
    async def load_mcp_tools(
        mcp_config: Dict[str, Any],
        timeout_seconds: float = 30.0
    ) -> Optional[MultiMCPTools]:
        """
        Load MCP tools from config

        Args:
            mcp_config: MCP server configuration dict
            timeout_seconds: Connection timeout

        Returns:
            MultiMCPTools instance or None if no servers configured
        """
        server_params = MCPAdapter.create_server_params(mcp_config)

        if not server_params:
            return None

        return MultiMCPTools(
            server_params_list=server_params,
            timeout_seconds=timeout_seconds
        )
