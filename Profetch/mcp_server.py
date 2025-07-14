# === Inject local mcp_lib into Python path so Claude can find it ===
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_lib"))

# === Now import MCP classes ===
from mcp.server.fastmcp import FastMCP
from bridge import Bridge
import asyncio

bridge = Bridge()
mcp = FastMCP("UniPROscope MCP")

# === Define MCP tools ===

@mcp.tool()
async def get_gene_info(gene_symbol: str) -> dict:
    """Fetch detailed UniProt information for a human gene symbol."""
    return await bridge.get_gene_info(gene_symbol)

@mcp.tool()
async def get_protein_expression(gene_symbol: str) -> str:
    """Get a summary of the protein's function and expression for a given gene symbol."""
    return await bridge.get_protein_expression(gene_symbol)

@mcp.tool()
async def get_subcellular_location(gene_symbol: str) -> list:
    """Get all known subcellular locations for a gene product."""
    return await bridge.get_subcellular_location(gene_symbol)

# === Entry point ===

if __name__ == "__main__":
    if "--serve" in sys.argv:
        mcp.run()
