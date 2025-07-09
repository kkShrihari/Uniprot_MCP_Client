"""
Main module for Uniport_MCP_Client.
"""


from .mcp_server import MCPServer






def main() -> None:
    """Main entry point for MCP server."""
    server = MCPServer()
    server.run()



if __name__ == "__main__":
    
    main()
     